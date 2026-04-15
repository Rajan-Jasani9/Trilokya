"""
Clone database data between environments.

Usage:
  # On source environment (current data)
  python scripts/clone_db_data.py export --out db_snapshot.json

  # On target environment (empty DB)
  python scripts/clone_db_data.py import --in db_snapshot.json
"""

import argparse
import enum
import json
import sys
from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import Base, SessionLocal, engine  # noqa: E402
from app import models  # noqa: F401, E402  # Ensure models register into Base metadata


def _json_default(value: Any) -> Any:
    if isinstance(value, datetime):
        return {"__type__": "datetime", "value": value.isoformat()}
    if isinstance(value, date):
        return {"__type__": "date", "value": value.isoformat()}
    if isinstance(value, time):
        return {"__type__": "time", "value": value.isoformat()}
    if isinstance(value, Decimal):
        return {"__type__": "decimal", "value": str(value)}
    if isinstance(value, enum.Enum):
        return {"__type__": "enum", "value": value.value}
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _json_object_hook(value: Dict[str, Any]) -> Any:
    type_name = value.get("__type__")
    if not type_name:
        return value
    raw = value.get("value")
    if type_name == "datetime":
        return datetime.fromisoformat(raw)
    if type_name == "date":
        return date.fromisoformat(raw)
    if type_name == "time":
        return time.fromisoformat(raw)
    if type_name == "decimal":
        return Decimal(raw)
    if type_name == "enum":
        # Store enum payload as raw value; SQLAlchemy Enum columns accept this.
        return raw
    return value


def export_data(output_path: Path) -> None:
    snapshot: Dict[str, Any] = {
        "meta": {
            "exported_at": datetime.utcnow().isoformat() + "Z",
            "database_url": str(engine.url).replace(str(engine.url.password or ""), "***")
            if engine.url.password
            else str(engine.url),
        },
        "tables": [],
    }

    with engine.connect() as conn:
        for table in Base.metadata.sorted_tables:
            rows = [dict(row) for row in conn.execute(table.select()).mappings().all()]
            snapshot["tables"].append(
                {
                    "name": table.name,
                    "row_count": len(rows),
                    "rows": rows,
                }
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(snapshot, default=_json_default, indent=2), encoding="utf-8")

    total_rows = sum(table["row_count"] for table in snapshot["tables"])
    print(f"Exported {total_rows} rows across {len(snapshot['tables'])} tables.")
    print(f"Snapshot written to: {output_path}")


def import_data(input_path: Path, truncate_existing: bool = False) -> None:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    payload = json.loads(input_path.read_text(encoding="utf-8"), object_hook=_json_object_hook)
    tables_payload: List[Dict[str, Any]] = payload.get("tables", [])

    db: Session = SessionLocal()
    try:
        Base.metadata.create_all(bind=engine)

        if truncate_existing:
            # Reverse order to satisfy FK constraints while deleting.
            for table in reversed(Base.metadata.sorted_tables):
                db.execute(table.delete())
            db.flush()

        table_map = Base.metadata.tables
        inserted = 0
        for table_payload in tables_payload:
            table_name = table_payload["name"]
            rows = table_payload.get("rows", [])
            if not rows:
                continue

            table = table_map.get(table_name)
            if table is None:
                print(f"Skipping unknown table from snapshot: {table_name}")
                continue

            db.execute(table.insert(), rows)
            inserted += len(rows)

        db.commit()

        # Best-effort sequence alignment for PostgreSQL after explicit-id insert.
        if engine.dialect.name == "postgresql":
            for table in Base.metadata.sorted_tables:
                pk_cols = list(table.primary_key.columns)
                if len(pk_cols) != 1:
                    continue
                pk_col = pk_cols[0]
                if not isinstance(pk_col.type.python_type, type):
                    continue
                if pk_col.type.python_type is not int:
                    continue
                db.execute(
                    text(
                        "SELECT setval(pg_get_serial_sequence(:table_name, :column_name), "
                        "COALESCE((SELECT MAX(" + pk_col.name + ") FROM " + table.name + "), 1), true)"
                    ),
                    {"table_name": table.name, "column_name": pk_col.name},
                )
            db.commit()

        print(f"Imported {inserted} rows from {input_path}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Export/import database data snapshot.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    export_parser = subparsers.add_parser("export", help="Export DB data to JSON snapshot.")
    export_parser.add_argument("--out", required=True, help="Output snapshot path, e.g. db_snapshot.json")

    import_parser = subparsers.add_parser("import", help="Import DB data snapshot into current DB.")
    import_parser.add_argument("--in", dest="input_file", required=True, help="Input snapshot path.")
    import_parser.add_argument(
        "--truncate-existing",
        action="store_true",
        help="Delete all existing data in known tables before importing.",
    )

    args = parser.parse_args()

    if args.command == "export":
        export_data(Path(args.out).resolve())
    elif args.command == "import":
        import_data(Path(args.input_file).resolve(), truncate_existing=args.truncate_existing)


if __name__ == "__main__":
    main()
