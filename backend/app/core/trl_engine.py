from sqlalchemy.orm import Session
from app.models import CTE, CTETRLAssessment, TRLResponse, TRLQuestion, TRLDefinition, Project, ProjectTRLOverride
from app.models.cte import AssessmentStatus
from app.models.trl import TRLResponseAnswer


def compute_cte_trl(db: Session, cte_id: int) -> int:
    """
    Compute current TRL for a CTE.
    Returns the highest TRL level where:
    - All required questions satisfy completion rule
    - Assessment is approved
    - Evidence requirements met (if configured)
    """
    cte = db.query(CTE).filter(CTE.id == cte_id).first()
    if not cte:
        return 0
    
    # Get all approved assessments, ordered by level descending
    assessments = db.query(CTETRLAssessment).filter(
        CTETRLAssessment.cte_id == cte_id,
        CTETRLAssessment.status == AssessmentStatus.APPROVED
    ).order_by(CTETRLAssessment.trl_level.desc()).all()
    
    if not assessments:
        return 0
    
    # Check each assessment from highest to lowest
    for assessment in assessments:
        if is_trl_level_complete(db, assessment):
            return assessment.trl_level
    
    return 0


def is_trl_level_complete(db: Session, assessment: CTETRLAssessment) -> bool:
    """
    Check if a TRL assessment level is complete.
    Completion rule: Configurable (100% Yes, ≥80% Yes, weighted scoring)
    """
    # Get TRL definition
    trl_def = db.query(TRLDefinition).filter(
        TRLDefinition.level == assessment.trl_level,
        TRLDefinition.is_active == True
    ).first()
    
    if not trl_def:
        return False
    
    # Get all questions for this TRL level
    questions = db.query(TRLQuestion).filter(
        TRLQuestion.trl_definition_id == trl_def.id
    ).all()
    
    if not questions:
        return False
    
    # Get all responses for this assessment
    responses = db.query(TRLResponse).filter(
        TRLResponse.cte_trl_assessment_id == assessment.id
    ).all()
    
    response_map = {r.trl_question_id: r for r in responses}
    
    # Check completion rule (default: all required questions must be Yes)
    required_questions = [q for q in questions if q.is_required]
    
    if not required_questions:
        return True
    
    # Check if all required questions are answered with Yes
    for question in required_questions:
        response = response_map.get(question.id)
        if not response or response.answer != TRLResponseAnswer.YES:
            return False
        
        # Check evidence requirement if configured
        if question.evidence_required:
            evidence_items = response.evidence_items
            if not evidence_items:
                return False
    
    return True


def compute_project_trl(db: Session, project_id: int) -> int:
    """
    Compute project TRL.
    Default: MIN(CTE TRLs) across all CTEs
    Alternative: Weighted average (if CTEs have weights)
    Override: Manual override by Manager/SuperAdmin
    """
    # Check for manual override
    override = db.query(ProjectTRLOverride).filter(
        ProjectTRLOverride.project_id == project_id
    ).order_by(ProjectTRLOverride.created_at.desc()).first()
    
    if override:
        return override.trl_value
    
    # Get all CTEs for project
    ctes = db.query(CTE).filter(CTE.project_id == project_id).all()
    
    if not ctes:
        return 0
    
    # Compute TRL for each CTE
    cte_trls = []
    for cte in ctes:
        cte_trl = compute_cte_trl(db, cte.id)
        if cte_trl > 0:
            cte_trls.append(cte_trl)
    
    if not cte_trls:
        return 0
    
    # Default: MIN(CTE TRLs)
    return min(cte_trls)


def compute_project_target_trl(db: Session, project_id: int) -> int:
    """
    Compute project Target TRL.
    Logic: MIN(Target TRL of all critical CTEs)
    """
    # Get all CTEs for project
    ctes = db.query(CTE).filter(CTE.project_id == project_id).all()
    
    if not ctes:
        return None
    
    # Get all CTEs with target_trl set
    cte_target_trls = [cte.target_trl for cte in ctes if cte.target_trl is not None]
    
    if not cte_target_trls:
        return None
    
    # Return minimum of all CTE target TRLs
    return min(cte_target_trls)


def can_unlock_trl_level(db: Session, cte_id: int, target_level: int) -> bool:
    """
    Check if a TRL level can be unlocked (TRL-N+1 locked until TRL-N is complete and approved)
    """
    if target_level <= 1:
        return True
    
    # Check if previous level is complete and approved
    prev_assessment = db.query(CTETRLAssessment).filter(
        CTETRLAssessment.cte_id == cte_id,
        CTETRLAssessment.trl_level == target_level - 1,
        CTETRLAssessment.status == AssessmentStatus.APPROVED
    ).first()
    
    if not prev_assessment:
        return False
    
    return is_trl_level_complete(db, prev_assessment)
