from typing import Optional, Dict
from sqlalchemy.orm import Session
from app.models import (
    CTE,
    CTETRLAssessment,
    CTEIRLAssessment,
    CTEMRLAssessment,
    TRLDefinition,
    TRLQuestion,
    TRLResponse,
    IRLDefinition,
    IRLQuestion,
    IRLResponse,
    MRLDefinition,
    MRLQuestion,
    MRLResponse,
    TRLCouplingConfig,
    ReadinessSettings,
)
from app.models.cte import AssessmentStatus
from app.models.trl import TRLResponseAnswer


def _is_level_complete(questions, responses_map) -> bool:
    required_questions = [q for q in questions if q.is_required]
    if not required_questions:
        return True
    for question in required_questions:
        response = responses_map.get(question.id)
        if not response or response.answer != TRLResponseAnswer.YES:
            return False
        if question.evidence_required and not response.evidence_text:
            return False
    return True


def compute_cte_trl(db: Session, cte_id: int) -> int:
    assessments = db.query(CTETRLAssessment).filter(
        CTETRLAssessment.cte_id == cte_id,
        CTETRLAssessment.status == AssessmentStatus.APPROVED
    ).order_by(CTETRLAssessment.trl_level.desc()).all()
    for assessment in assessments:
        definition = db.query(TRLDefinition).filter(TRLDefinition.level == assessment.trl_level, TRLDefinition.is_active == True).first()
        if not definition:
            continue
        questions = db.query(TRLQuestion).filter(TRLQuestion.trl_definition_id == definition.id).all()
        responses = db.query(TRLResponse).filter(TRLResponse.cte_trl_assessment_id == assessment.id).all()
        if _is_level_complete(questions, {r.trl_question_id: r for r in responses}):
            return assessment.trl_level
    return 0


def compute_cte_irl(db: Session, cte_id: int) -> int:
    assessments = db.query(CTEIRLAssessment).filter(
        CTEIRLAssessment.cte_id == cte_id,
        CTEIRLAssessment.status == AssessmentStatus.APPROVED
    ).order_by(CTEIRLAssessment.irl_level.desc()).all()
    for assessment in assessments:
        definition = db.query(IRLDefinition).filter(IRLDefinition.level == assessment.irl_level, IRLDefinition.is_active == True).first()
        if not definition:
            continue
        questions = db.query(IRLQuestion).filter(IRLQuestion.irl_definition_id == definition.id).all()
        responses = db.query(IRLResponse).filter(IRLResponse.cte_irl_assessment_id == assessment.id).all()
        if _is_level_complete(questions, {r.irl_question_id: r for r in responses}):
            return assessment.irl_level
    return 0


def compute_cte_mrl(db: Session, cte_id: int) -> int:
    assessments = db.query(CTEMRLAssessment).filter(
        CTEMRLAssessment.cte_id == cte_id,
        CTEMRLAssessment.status == AssessmentStatus.APPROVED
    ).order_by(CTEMRLAssessment.mrl_level.desc()).all()
    for assessment in assessments:
        definition = db.query(MRLDefinition).filter(MRLDefinition.level == assessment.mrl_level, MRLDefinition.is_active == True).first()
        if not definition:
            continue
        questions = db.query(MRLQuestion).filter(MRLQuestion.mrl_definition_id == definition.id).all()
        responses = db.query(MRLResponse).filter(MRLResponse.cte_mrl_assessment_id == assessment.id).all()
        if _is_level_complete(questions, {r.mrl_question_id: r for r in responses}):
            return assessment.mrl_level
    return 0


def compute_cte_srl(db: Session, cte_id: int) -> int:
    return min(compute_cte_trl(db, cte_id), compute_cte_irl(db, cte_id), compute_cte_mrl(db, cte_id))


def _project_min(db: Session, project_id: int, getter) -> int:
    ctes = db.query(CTE).filter(CTE.project_id == project_id).all()
    if not ctes:
        return 0
    levels = [getter(db, cte.id) for cte in ctes]
    levels = [x for x in levels if x > 0]
    return min(levels) if levels else 0


def compute_project_irl(db: Session, project_id: int) -> int:
    return _project_min(db, project_id, compute_cte_irl)


def compute_project_mrl(db: Session, project_id: int) -> int:
    return _project_min(db, project_id, compute_cte_mrl)


def compute_project_srl(db: Session, project_id: int, project_trl: int) -> int:
    return min(project_trl, compute_project_irl(db, project_id), compute_project_mrl(db, project_id))


def get_coupling_requirement(db: Session, trl_level: int) -> Dict[str, int]:
    cfg = db.query(TRLCouplingConfig).filter(TRLCouplingConfig.trl_level == trl_level).first()
    if cfg:
        return {"min_irl": cfg.min_irl, "min_mrl": cfg.min_mrl}
    # conservative defaults: keep one level behind TRL
    base = max(1, trl_level - 1)
    return {"min_irl": base, "min_mrl": base}


def get_strict_mode_default(db: Session) -> bool:
    settings = db.query(ReadinessSettings).first()
    return settings.strict_mode_default if settings else False
