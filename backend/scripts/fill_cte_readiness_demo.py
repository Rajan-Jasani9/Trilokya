"""
Populate demo readiness progressions for all existing CTEs.

This script assigns randomized TRL, IRL, and MRL levels (>= 1) per CTE and
creates complete APPROVED assessments with required YES responses so computed
readiness is never zero for demo purposes.
"""

import argparse
import random
import sys
from pathlib import Path
from typing import List

from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal  # noqa: E402
from app.models import (  # noqa: E402
    CTE,
    User,
    CTETRLAssessment,
    CTEIRLAssessment,
    CTEMRLAssessment,
    TRLDefinition,
    TRLQuestion,
    TRLResponse,
    EvidenceItem,
    IRLDefinition,
    IRLQuestion,
    IRLResponse,
    MRLDefinition,
    MRLQuestion,
    MRLResponse,
)
from app.models.cte import AssessmentStatus  # noqa: E402
from app.models.trl import TRLResponseAnswer, EvidenceType  # noqa: E402


def _pick_assessor_id(db: Session, cte: CTE) -> int:
    if cte.project and cte.project.created_by:
        return cte.project.created_by
    user = db.query(User).filter(User.is_active == True).order_by(User.id.asc()).first()
    if not user:
        raise RuntimeError("No active user found. Create at least one user before running this script.")
    return user.id


def _level_definitions_available(db: Session) -> bool:
    trl_count = db.query(TRLDefinition).filter(TRLDefinition.level.between(1, 9)).count()
    irl_count = db.query(IRLDefinition).filter(IRLDefinition.level.between(1, 9)).count()
    mrl_count = db.query(MRLDefinition).filter(MRLDefinition.level.between(1, 9)).count()
    return trl_count > 0 and irl_count > 0 and mrl_count > 0


def _reset_cte_readiness(db: Session, cte_id: int) -> None:
    db.query(CTETRLAssessment).filter(CTETRLAssessment.cte_id == cte_id).delete(synchronize_session=False)
    db.query(CTEIRLAssessment).filter(CTEIRLAssessment.cte_id == cte_id).delete(synchronize_session=False)
    db.query(CTEMRLAssessment).filter(CTEMRLAssessment.cte_id == cte_id).delete(synchronize_session=False)


def _create_trl_progression(db: Session, cte: CTE, assessed_by: int, level: int, rng: random.Random) -> None:
    for step in range(1, level + 1):
        _create_trl_level(db, cte, assessed_by, step, rng)


def _create_trl_level(db: Session, cte: CTE, assessed_by: int, level: int, rng: random.Random) -> None:
    definition = db.query(TRLDefinition).filter(TRLDefinition.level == level, TRLDefinition.is_active == True).first()
    if not definition:
        raise RuntimeError(f"Missing active TRL definition for level {level}")

    assessment = CTETRLAssessment(
        cte_id=cte.id,
        trl_level=level,
        assessed_by=assessed_by,
        status=AssessmentStatus.APPROVED,
        confidence_score=round(rng.uniform(0.7, 0.98), 2),
        notes=f"Demo randomized TRL assessment generated at level {level}.",
    )
    db.add(assessment)
    db.flush()

    questions: List[TRLQuestion] = (
        db.query(TRLQuestion)
        .filter(TRLQuestion.trl_definition_id == definition.id)
        .order_by(TRLQuestion.question_order.asc())
        .all()
    )
    for question in questions:
        answer = TRLResponseAnswer.YES if question.is_required else rng.choice(
            [TRLResponseAnswer.YES, TRLResponseAnswer.NO, TRLResponseAnswer.NA]
        )
        evidence = (
            f"Demo evidence for TRL-{level} Q{question.question_order}."
            if question.evidence_required and answer == TRLResponseAnswer.YES
            else None
        )
        trl_response = TRLResponse(
            cte_trl_assessment_id=assessment.id,
            trl_question_id=question.id,
            answer=answer,
            evidence_text=evidence,
            confidence_score=round(rng.uniform(0.65, 0.99), 2),
        )
        db.add(trl_response)
        db.flush()
        if question.evidence_required and answer == TRLResponseAnswer.YES:
            db.add(
                EvidenceItem(
                    trl_response_id=trl_response.id,
                    evidence_type=EvidenceType.LINK,
                    external_url=f"https://demo.local/trl/{cte.id}/{level}/{question.id}",
                    file_name=f"demo-trl-{cte.id}-{level}-{question.id}.txt",
                    uploaded_by=assessed_by,
                )
            )


def _create_irl_progression(db: Session, cte: CTE, assessed_by: int, level: int, rng: random.Random) -> None:
    for step in range(1, level + 1):
        _create_irl_level(db, cte, assessed_by, step, rng)


def _create_irl_level(db: Session, cte: CTE, assessed_by: int, level: int, rng: random.Random) -> None:
    definition = db.query(IRLDefinition).filter(IRLDefinition.level == level, IRLDefinition.is_active == True).first()
    if not definition:
        raise RuntimeError(f"Missing active IRL definition for level {level}")

    assessment = CTEIRLAssessment(
        cte_id=cte.id,
        irl_level=level,
        assessed_by=assessed_by,
        status=AssessmentStatus.APPROVED,
        confidence_score=round(rng.uniform(0.7, 0.98), 2),
        notes=f"Demo randomized IRL assessment generated at level {level}.",
    )
    db.add(assessment)
    db.flush()

    questions: List[IRLQuestion] = (
        db.query(IRLQuestion)
        .filter(IRLQuestion.irl_definition_id == definition.id)
        .order_by(IRLQuestion.question_order.asc())
        .all()
    )
    for question in questions:
        answer = TRLResponseAnswer.YES if question.is_required else rng.choice(
            [TRLResponseAnswer.YES, TRLResponseAnswer.NO, TRLResponseAnswer.NA]
        )
        evidence = (
            f"Demo evidence for IRL-{level} Q{question.question_order}."
            if question.evidence_required and answer == TRLResponseAnswer.YES
            else None
        )
        db.add(
            IRLResponse(
                cte_irl_assessment_id=assessment.id,
                irl_question_id=question.id,
                answer=answer,
                evidence_text=evidence,
                confidence_score=round(rng.uniform(0.65, 0.99), 2),
            )
        )


def _create_mrl_progression(db: Session, cte: CTE, assessed_by: int, level: int, rng: random.Random) -> None:
    for step in range(1, level + 1):
        _create_mrl_level(db, cte, assessed_by, step, rng)


def _create_mrl_level(db: Session, cte: CTE, assessed_by: int, level: int, rng: random.Random) -> None:
    definition = db.query(MRLDefinition).filter(MRLDefinition.level == level, MRLDefinition.is_active == True).first()
    if not definition:
        raise RuntimeError(f"Missing active MRL definition for level {level}")

    assessment = CTEMRLAssessment(
        cte_id=cte.id,
        mrl_level=level,
        assessed_by=assessed_by,
        status=AssessmentStatus.APPROVED,
        confidence_score=round(rng.uniform(0.7, 0.98), 2),
        notes=f"Demo randomized MRL assessment generated at level {level}.",
    )
    db.add(assessment)
    db.flush()

    questions: List[MRLQuestion] = (
        db.query(MRLQuestion)
        .filter(MRLQuestion.mrl_definition_id == definition.id)
        .order_by(MRLQuestion.question_order.asc())
        .all()
    )
    for question in questions:
        answer = TRLResponseAnswer.YES if question.is_required else rng.choice(
            [TRLResponseAnswer.YES, TRLResponseAnswer.NO, TRLResponseAnswer.NA]
        )
        evidence = (
            f"Demo evidence for MRL-{level} Q{question.question_order}."
            if question.evidence_required and answer == TRLResponseAnswer.YES
            else None
        )
        db.add(
            MRLResponse(
                cte_mrl_assessment_id=assessment.id,
                mrl_question_id=question.id,
                answer=answer,
                evidence_text=evidence,
                confidence_score=round(rng.uniform(0.65, 0.99), 2),
            )
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Fill all CTEs with randomized non-zero TRL/IRL/MRL progressions.")
    parser.add_argument("--seed", type=int, default=None, help="Optional random seed for reproducible output.")
    parser.add_argument("--min-level", type=int, default=4, help="Minimum random level to assign for all domains (default: 4).")
    parser.add_argument("--max-level", type=int, default=9, help="Maximum random level to assign for all domains (default: 9).")
    parser.add_argument("--min-trl", type=int, default=None, help="Optional TRL-specific minimum override.")
    parser.add_argument("--max-trl", type=int, default=None, help="Optional TRL-specific maximum override.")
    parser.add_argument("--min-irl", type=int, default=None, help="Optional IRL-specific minimum override.")
    parser.add_argument("--max-irl", type=int, default=None, help="Optional IRL-specific maximum override.")
    parser.add_argument("--min-mrl", type=int, default=None, help="Optional MRL-specific minimum override.")
    parser.add_argument("--max-mrl", type=int, default=None, help="Optional MRL-specific maximum override.")
    args = parser.parse_args()

    trl_min = args.min_trl if args.min_trl is not None else args.min_level
    trl_max = args.max_trl if args.max_trl is not None else args.max_level
    irl_min = args.min_irl if args.min_irl is not None else args.min_level
    irl_max = args.max_irl if args.max_irl is not None else args.max_level
    mrl_min = args.min_mrl if args.min_mrl is not None else args.min_level
    mrl_max = args.max_mrl if args.max_mrl is not None else args.max_level

    ranges = {
        "TRL": (trl_min, trl_max),
        "IRL": (irl_min, irl_max),
        "MRL": (mrl_min, mrl_max),
    }
    for name, (mn, mx) in ranges.items():
        if mn < 1 or mx > 9 or mn > mx:
            raise ValueError(
                f"Invalid {name} range [{mn}, {mx}]. Allowed range is 1..9 and min must be <= max."
            )

    rng = random.Random(args.seed)
    db = SessionLocal()

    try:
        if not _level_definitions_available(db):
            raise RuntimeError(
                "Missing readiness definitions. Run init_trl.py, init_irl.py, and init_mrl.py before this script."
            )

        ctes = db.query(CTE).order_by(CTE.id.asc()).all()
        if not ctes:
            print("No CTEs found. Nothing to update.")
            return

        updated = 0
        for cte in ctes:
            assessed_by = _pick_assessor_id(db, cte)
            _reset_cte_readiness(db, cte.id)

            trl_level = rng.randint(trl_min, trl_max)
            irl_level = rng.randint(irl_min, irl_max)
            mrl_level = rng.randint(mrl_min, mrl_max)

            _create_trl_progression(db, cte, assessed_by, trl_level, rng)
            _create_irl_progression(db, cte, assessed_by, irl_level, rng)
            _create_mrl_progression(db, cte, assessed_by, mrl_level, rng)
            updated += 1

        db.commit()
        print(f"Demo readiness data generated for {updated} CTE(s).")
        print("All updated CTEs now have non-zero TRL, IRL, and MRL progression records.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
