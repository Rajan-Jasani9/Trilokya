"""
TRL Definitions and Questions initialization script.
Aligned with DRDO / NASA / IIT TRL assessment doctrine.
"""

import sys
from pathlib import Path
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import TRLDefinition, TRLQuestion


TRL_DEFINITIONS = {
    1: {
        "name": "Basic Principles Observed",
        "description": (
            "Fundamental scientific principles underlying the technology have been "
            "identified, observed, and reported through basic research."
        ),
    },
    2: {
        "name": "Technology Concept Formulated",
        "description": (
            "Practical applications of the technology are identified and the "
            "technology concept or application is formulated."
        ),
    },
    3: {
        "name": "Experimental Proof of Concept",
        "description": (
            "Analytical and experimental studies are performed to validate the "
            "feasibility of the technology concept."
        ),
    },
    4: {
        "name": "Technology Validated in Laboratory",
        "description": (
            "Components or breadboards are developed and validated in a laboratory "
            "environment."
        ),
    },
    5: {
        "name": "Technology Validated in Relevant Environment",
        "description": (
            "Technology is tested and validated in a relevant environment that "
            "approximates operational conditions."
        ),
    },
    6: {
        "name": "Technology Demonstrated in Relevant Environment",
        "description": (
            "A representative prototype is demonstrated in a relevant end-to-end "
            "environment."
        ),
    },
    7: {
        "name": "System Prototype Demonstrated in Operational Environment",
        "description": (
            "A system prototype is demonstrated in an operational environment."
        ),
    },
    8: {
        "name": "System Complete and Qualified",
        "description": (
            "The actual system is completed, integrated, and qualified through "
            "testing and validation."
        ),
    },
    9: {
        "name": "Actual System Proven in Operational Environment",
        "description": (
            "The system is proven through successful mission or operational use."
        ),
    },
}


# (question_text, is_required, evidence_required, weight)
TRL_QUESTIONS = {
    1: [
        ("Have fundamental scientific principles relevant to this technology been identified?", True, False, 1.0),
        ("Have these principles been examined through theoretical or observational studies?", True, False, 1.0),
        ("Have the observations or principles been documented in reports or publications?", True, False, 1.0),
    ],
    2: [
        ("Have potential applications of the technology been identified?", True, False, 1.0),
        ("Has a technology concept or hypothesis been formulated?", True, False, 1.0),
        ("Have preliminary models or conceptual designs been created?", False, False, 0.8),
    ],
    3: [
        ("Have analytical studies been conducted to validate the technology concept?", True, True, 1.0),
        ("Have laboratory experiments demonstrated proof of concept?", True, True, 1.0),
        ("Have key technical challenges been identified and documented?", True, True, 1.0),
        ("Are experimental results recorded and reproducible?", False, True, 0.8),
    ],
    4: [
        ("Has a working component or breadboard been developed?", True, True, 1.0),
        ("Has the technology been validated through laboratory testing?", True, True, 1.0),
        ("Do test results confirm expected performance characteristics?", True, True, 1.0),
        ("Are laboratory test reports and data available?", False, True, 0.8),
    ],
    5: [
        ("Has the technology been tested in a relevant (simulated or field) environment?", True, True, 1.0),
        ("Does the technology perform reliably under relevant conditions?", True, True, 1.0),
        ("Have limitations and risks been identified in the relevant environment?", True, True, 1.0),
        ("Are field or pilot test reports available?", False, True, 0.9),
    ],
    6: [
        ("Has a representative prototype been developed?", True, True, 1.0),
        ("Has the prototype been demonstrated in a relevant end-to-end environment?", True, True, 1.0),
        ("Does the prototype meet defined performance requirements?", True, True, 1.0),
        ("Have system-level integration issues been identified and addressed?", False, True, 0.8),
    ],
    7: [
        ("Has a system prototype been demonstrated in an operational environment?", True, True, 1.0),
        ("Does the system meet operational performance requirements?", True, True, 1.0),
        ("Have operational constraints and risks been validated?", True, True, 1.0),
        ("Are operational test and evaluation reports available?", False, True, 0.9),
    ],
    8: [
        ("Has the system been fully integrated and completed?", True, True, 1.0),
        ("Has the system been qualified through formal testing and validation?", True, True, 1.0),
        ("Does the system comply with all specified requirements and standards?", True, True, 1.0),
        ("Are certification or qualification documents available?", False, True, 0.9),
    ],
    9: [
        ("Has the system been successfully deployed in an operational setting?", True, True, 1.0),
        ("Has the system demonstrated sustained operational performance?", True, True, 1.0),
        ("Are there documented outcomes from real-world missions or operations?", True, True, 1.0),
        ("Have lessons learned and operational feedback been captured?", False, True, 0.8),
    ],
}


def create_trl_definitions(db: Session):
    created = {}

    for level in range(1, 10):
        existing = db.query(TRLDefinition).filter_by(level=level).first()
        if existing:
            created[level] = existing
            continue

        trl_def = TRLDefinition(
            level=level,
            name=TRL_DEFINITIONS[level]["name"],
            description=TRL_DEFINITIONS[level]["description"],
            evidence_required=(level >= 3),
            min_confidence=None,
            is_active=True,
        )
        db.add(trl_def)
        db.flush()

        for order, (text, required, evidence, weight) in enumerate(TRL_QUESTIONS[level], start=1):
            db.add(
                TRLQuestion(
                    trl_definition_id=trl_def.id,
                    question_text=text,
                    question_order=order,
                    is_required=required,
                    evidence_required=evidence,
                    weight=weight,
                )
            )

        created[level] = trl_def

    return created


def main():
    db = SessionLocal()
    try:
        create_trl_definitions(db)
        db.commit()
        print("✓ TRL definitions and questions initialized successfully.")
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
