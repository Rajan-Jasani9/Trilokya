"""
Load technology_foresight_seed.json into OrgUnit, Technology, Project,
ProjectTechnology, ProjectOrgUnit, and CTE.

Prerequisites: run init_db.py (users, roles) and optionally init_technologies.py
for SVG icons. Technologies missing from DB are created without icons.

Usage (from backend/, use venv):
  .\\venv\\Scripts\\python.exe scripts\\load_technology_foresight.py
  .\\venv\\Scripts\\python.exe scripts\\load_technology_foresight.py --dry-run
  (or scripts\\run_load_foresight.bat)
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session

from app.database import SessionLocal, engine, Base
from app.models import (
    OrgUnit,
    Technology,
    Project,
    ProjectOrgUnit,
    ProjectTechnology,
    CTE,
    User,
    Role,
    UserRole,
)
from app.models.project import ProjectCategory
from app.core.trl_engine import compute_project_target_trl


SEED_PATH = Path(__file__).parent.parent / "data" / "technology_foresight_seed.json"


def _get_seed_creator_id(db: Session) -> int:
    """Prefer SuperAdmin, else first user."""
    super_role = db.query(Role).filter(Role.name == "SuperAdmin").first()
    if super_role:
        ur = (
            db.query(UserRole)
            .filter(UserRole.role_id == super_role.id)
            .first()
        )
        if ur:
            return ur.user_id
    u = db.query(User).order_by(User.id).first()
    if not u:
        raise RuntimeError("No users in database. Run init_db.py first.")
    return u.id


def ensure_org_units(db: Session, rows: list, dry: bool) -> dict[str, OrgUnit]:
    by_code: dict[str, OrgUnit] = {}

    for r in rows:
        code = r["code"]
        existing = db.query(OrgUnit).filter(OrgUnit.code == code).first()
        if existing:
            by_code[code] = existing
            continue
        if dry:
            print(f"  [dry-run] would create OrgUnit {code}: {r['name']}")
            continue
        hq = db.query(OrgUnit).filter(OrgUnit.code == "DRDO-HQ").first()
        parent_id = None if code == "DRDO-HQ" else (hq.id if hq else None)
        ou = OrgUnit(
            code=code,
            name=r["name"],
            org_type=r["org_type"],
            parent_id=parent_id,
        )
        db.add(ou)
        db.flush()
        by_code[code] = ou
        print(f"  [+] OrgUnit {code}")

    if not dry:
        db.commit()

    for r in rows:
        code = r["code"]
        if code not in by_code:
            by_code[code] = db.query(OrgUnit).filter(OrgUnit.code == code).first()

    return by_code


def ensure_technology(db: Session, name: str, display_order: int, dry: bool) -> Technology | None:
    t = db.query(Technology).filter(Technology.name == name).first()
    if t:
        return t
    if dry:
        print(f"  [dry-run] would create Technology: {name}")
        return None
    t = Technology(
        name=name,
        description=None,
        icon_filename=None,
        is_active=True,
        display_order=display_order,
    )
    db.add(t)
    db.flush()
    print(f"  [+] Technology: {name}")
    return t


def load_programmes(
    db: Session,
    programmes: list,
    org_by_code: dict[str, OrgUnit],
    creator_id: int,
    dry: bool,
):
    for idx, prog in enumerate(programmes):
        tech_name = prog["technology_name"]
        p = prog["project"]
        code = p["code"]

        existing_proj = db.query(Project).filter(Project.code == code).first()
        if existing_proj:
            print(f"  [skip] Project {code} already exists")
            continue

        if dry:
            ensure_technology(db, tech_name, idx, True)
            print(f"  [dry-run] would create Project {code} + {len(prog['ctes'])} CTEs")
            continue

        t = ensure_technology(db, tech_name, idx, False)
        if not t:
            continue

        cat = ProjectCategory(p["category"])
        start = date.fromisoformat(p["start_date"])
        end = date.fromisoformat(p["end_date"]) if p.get("end_date") else None

        project = Project(
            code=code,
            name=p["name"],
            description=p.get("description"),
            category=cat,
            target_trl=p.get("target_trl"),
            start_date=start,
            end_date=end,
            created_by=creator_id,
        )
        db.add(project)
        db.flush()

        pt = ProjectTechnology(project_id=project.id, technology_id=t.id)
        db.add(pt)

        for oc in p.get("org_unit_codes", []):
            ou = org_by_code.get(oc)
            if not ou:
                print(f"  [warn] Unknown org_unit code {oc} for {code}")
                continue
            db.add(ProjectOrgUnit(project_id=project.id, org_unit_id=ou.id))

        for c in prog["ctes"]:
            db.add(
                CTE(
                    project_id=project.id,
                    code=c["code"],
                    name=c["name"],
                    description=c.get("description"),
                    category=c.get("category"),
                    target_trl=c.get("target_trl"),
                )
            )

        db.flush()
        computed = compute_project_target_trl(db, project.id)
        if computed is not None:
            project.target_trl = computed

        db.commit()
        print(f"  [+] Project {code} ({tech_name})")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not SEED_PATH.is_file():
        print(f"Missing {SEED_PATH}. Run: python scripts/write_foresight_json.py")
        sys.exit(1)

    data = json.loads(SEED_PATH.read_text(encoding="utf-8"))

    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        creator_id = _get_seed_creator_id(db)
        print(f"Using created_by user id={creator_id}")
        print("Ensuring org units...")
        org_by_code = ensure_org_units(db, data["org_units"], args.dry_run)

        print("Loading programmes...")
        load_programmes(db, data["programmes"], org_by_code, creator_id, args.dry_run)
        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
