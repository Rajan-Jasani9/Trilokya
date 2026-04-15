"""
MRL Definitions and Questions initialization script.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import MRLDefinition, MRLQuestion


MRL_DEFINITIONS = {
    1: {"name": "Manufacturing Feasibility Identified", "description": "Manufacturing concepts and risks identified."},
    2: {"name": "Manufacturing Concepts Evaluated", "description": "Candidate materials/processes screened with initial data."},
    3: {"name": "Manufacturing Proof of Concept", "description": "Process concept demonstrated on representative elements."},
    4: {"name": "Capability in Laboratory", "description": "Manufacturing methods repeatable in controlled settings."},
    5: {"name": "Pilot Process in Relevant Environment", "description": "Pilot line/process demonstrated with representative constraints."},
    6: {"name": "Low-Rate Production Readiness", "description": "Quality and supplier controls support low-rate output."},
    7: {"name": "Production Representative Capability", "description": "Stable throughput and quality under production-like demand."},
    8: {"name": "Full-Rate Production Qualified", "description": "Process fully qualified for target scale and quality."},
    9: {"name": "Full-Rate Production Proven", "description": "Sustained production performance meets contractual baselines."},
}

MRL_QUESTIONS = {
    1: [("Are key manufacturing risks identified with mitigation owners?", True, True, 1.0), ("Are critical materials/process options mapped to constraints?", True, True, 1.0)],
    2: [("Have candidate processes been screened with objective criteria?", True, True, 1.0), ("Are initial cost/yield assumptions documented and reviewed?", True, True, 1.0)],
    3: [("Has proof-of-concept manufacturing succeeded on representative parts?", True, True, 1.0), ("Are producibility concerns captured in design feedback?", True, True, 1.0)],
    4: [("Are process parameters controlled and repeatable in lab runs?", True, True, 1.0), ("Are inspection/verification methods defined for key characteristics?", True, True, 1.0)],
    5: [("Has pilot process been validated under relevant constraints and loads?", True, True, 1.0), ("Are supplier capability and lead-time risks actively managed?", True, True, 1.0)],
    6: [("Can low-rate production meet quality gates with traceability?", True, True, 1.0), ("Are NCR/rework metrics tracked with corrective actions?", True, True, 1.0)],
    7: [("Has production-representative throughput been demonstrated repeatedly?", True, True, 1.0), ("Are SPC and process-capability indices within required limits?", True, True, 1.0)],
    8: [("Is full-rate production process qualified with approved control plans?", True, True, 1.0), ("Are tooling, workforce, and supplier capacity validated for scale?", True, True, 1.0)],
    9: [("Do sustained production runs meet yield, cost, and schedule baselines?", True, True, 1.0), ("Are field returns/defects within acceptance thresholds over time?", True, True, 1.0)],
}


def main():
    db = SessionLocal()
    try:
        for level, meta in MRL_DEFINITIONS.items():
            definition = db.query(MRLDefinition).filter_by(level=level).first()
            if not definition:
                definition = MRLDefinition(level=level, name=meta["name"], description=meta["description"], evidence_required=True, is_active=True)
                db.add(definition)
                db.flush()
            else:
                definition.name = meta["name"]
                definition.description = meta["description"]

            db.query(MRLQuestion).filter(MRLQuestion.mrl_definition_id == definition.id).delete()
            for order, (text, required, evidence, weight) in enumerate(MRL_QUESTIONS[level], start=1):
                db.add(MRLQuestion(
                    mrl_definition_id=definition.id,
                    question_text=text,
                    question_order=order,
                    is_required=required,
                    evidence_required=evidence,
                    weight=weight,
                ))
        db.commit()
        print("MRL definitions and questions initialized.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
