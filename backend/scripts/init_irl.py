"""
IRL Definitions and Questions initialization script.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import IRLDefinition, IRLQuestion


IRL_DEFINITIONS = {
    1: {"name": "Interface Concepts Identified", "description": "Potential interfaces and dependencies are identified."},
    2: {"name": "Interface Requirements Drafted", "description": "Interface requirements documented and reviewed."},
    3: {"name": "Interface Design Baseline", "description": "Interface control documents baselined for subsystems."},
    4: {"name": "Lab Integration Demonstrated", "description": "Interface behavior validated in controlled integration tests."},
    5: {"name": "Relevant Environment Integration", "description": "Integration demonstrated in relevant operational conditions."},
    6: {"name": "System Integration Verified", "description": "Critical end-to-end mission threads verified."},
    7: {"name": "Pre-Operational Integration", "description": "Interoperability and failure handling validated at scale."},
    8: {"name": "Operational Integration Qualified", "description": "Integration qualified for production/fielding context."},
    9: {"name": "Operational Integration Proven", "description": "Sustained integrated operation with measured reliability."},
}

IRL_QUESTIONS = {
    1: [("Are all upstream/downstream interface partners identified?", True, True, 1.0), ("Are key external dependencies logged with owners?", True, True, 1.0)],
    2: [("Are measurable interface requirements defined (data, timing, protocols)?", True, True, 1.0), ("Are assumptions and constraints approved by stakeholders?", True, True, 1.0)],
    3: [("Is an interface control document baselined and versioned?", True, True, 1.0), ("Are change-control paths for interface updates established?", True, True, 1.0)],
    4: [("Have integration tests validated nominal and off-nominal paths in lab?", True, True, 1.0), ("Are interface defects triaged with closure evidence?", True, True, 1.0)],
    5: [("Is interface performance validated in relevant environment/load?", True, True, 1.0), ("Are interoperability risks with adjacent systems mitigated?", True, True, 1.0)],
    6: [("Are critical mission threads passing end-to-end with traceability?", True, True, 1.0), ("Are interface failures detectable and recoverable in-system?", True, True, 1.0)],
    7: [("Has multi-configuration integration been verified with representative variants?", True, True, 1.0), ("Are integration regressions controlled via CI/qualification suite?", True, True, 1.0)],
    8: [("Has pre-operational qualification validated integrated behavior and safety?", True, True, 1.0), ("Are configuration and release baselines frozen for deployment readiness?", True, True, 1.0)],
    9: [("Do operational reports show sustained integrated performance?", True, True, 1.0), ("Are interface incidents within agreed thresholds over sustained duration?", True, True, 1.0)],
}


def main():
    db = SessionLocal()
    try:
        for level, meta in IRL_DEFINITIONS.items():
            definition = db.query(IRLDefinition).filter_by(level=level).first()
            if not definition:
                definition = IRLDefinition(level=level, name=meta["name"], description=meta["description"], evidence_required=True, is_active=True)
                db.add(definition)
                db.flush()
            else:
                definition.name = meta["name"]
                definition.description = meta["description"]

            db.query(IRLQuestion).filter(IRLQuestion.irl_definition_id == definition.id).delete()
            for order, (text, required, evidence, weight) in enumerate(IRL_QUESTIONS[level], start=1):
                db.add(IRLQuestion(
                    irl_definition_id=definition.id,
                    question_text=text,
                    question_order=order,
                    is_required=required,
                    evidence_required=evidence,
                    weight=weight,
                ))
        db.commit()
        print("IRL definitions and questions initialized.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
