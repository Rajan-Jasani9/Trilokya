from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import CTE, CTETRLAssessment, TRLDefinition, TRLQuestion, TRLResponse, EvidenceItem, ProjectReadinessConfig
from app.schemas.cte import CTETRLAssessmentCreate, CTETRLAssessmentResponse
from app.schemas.trl import TRLDefinitionResponse, TRLQuestionResponse, TRLResponseCreate, TRLResponseResponse, AdvanceTRLRequest
from app.api.deps import get_current_active_user, check_cte_access
from app.models.cte import AssessmentStatus
from app.core.readiness_engine import compute_cte_irl, compute_cte_mrl, get_coupling_requirement, get_strict_mode_default

router = APIRouter()


@router.get("/ctes/{cte_id}/trl-assessments", response_model=List[CTETRLAssessmentResponse])
async def list_trl_assessments(
    cte_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List TRL assessments for a CTE"""
    await check_cte_access(cte_id)(current_user=current_user, db=db)
    
    assessments = db.query(CTETRLAssessment).filter(CTETRLAssessment.cte_id == cte_id).all()
    return assessments


@router.post("/ctes/{cte_id}/trl-assessments/{level}", response_model=CTETRLAssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_trl_assessment(
    cte_id: int,
    level: int,
    assessment_data: CTETRLAssessmentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Start a new TRL assessment"""
    await check_cte_access(cte_id)(current_user=current_user, db=db)
    
    # Check if assessment already exists
    existing = db.query(CTETRLAssessment).filter(
        CTETRLAssessment.cte_id == cte_id,
        CTETRLAssessment.trl_level == level
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TRL assessment for this level already exists"
        )
    
    assessment = CTETRLAssessment(
        cte_id=cte_id,
        trl_level=level,
        assessed_by=current_user.id,
        notes=assessment_data.notes,
        confidence_score=assessment_data.confidence_score,
        status=AssessmentStatus.DRAFT
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@router.get("/ctes/{cte_id}/trl-assessments/{level}/questions", response_model=List[TRLQuestionResponse])
async def get_trl_questions(
    cte_id: int,
    level: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get questions for a TRL level"""
    await check_cte_access(cte_id)(current_user=current_user, db=db)
    
    trl_def = db.query(TRLDefinition).filter(
        TRLDefinition.level == level,
        TRLDefinition.is_active == True
    ).first()
    
    if not trl_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TRL level {level} definition not found"
        )
    
    questions = db.query(TRLQuestion).filter(
        TRLQuestion.trl_definition_id == trl_def.id
    ).order_by(TRLQuestion.question_order).all()
    
    return questions


@router.post("/ctes/{cte_id}/trl-assessments/{level}/responses", response_model=TRLResponseResponse, status_code=status.HTTP_201_CREATED)
async def submit_trl_response(
    cte_id: int,
    level: int,
    response_data: TRLResponseCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Submit a TRL response"""
    await check_cte_access(cte_id)(current_user=current_user, db=db)
    
    # Get or create assessment
    assessment = db.query(CTETRLAssessment).filter(
        CTETRLAssessment.cte_id == cte_id,
        CTETRLAssessment.trl_level == level
    ).first()
    
    if not assessment:
        assessment = CTETRLAssessment(
            cte_id=cte_id,
            trl_level=level,
            assessed_by=current_user.id,
            status=AssessmentStatus.DRAFT
        )
        db.add(assessment)
        db.flush()
    
    # Check if response already exists
    existing = db.query(TRLResponse).filter(
        TRLResponse.cte_trl_assessment_id == assessment.id,
        TRLResponse.trl_question_id == response_data.trl_question_id
    ).first()
    
    if existing:
        # Update existing response
        existing.answer = response_data.answer
        existing.evidence_text = response_data.evidence_text
        existing.confidence_score = response_data.confidence_score
        response = existing
    else:
        # Create new response
        response = TRLResponse(
            cte_trl_assessment_id=assessment.id,
            trl_question_id=response_data.trl_question_id,
            answer=response_data.answer,
            evidence_text=response_data.evidence_text,
            confidence_score=response_data.confidence_score
        )
        db.add(response)
        db.flush()
    
    # Handle evidence items (will be handled by evidence route)
    db.commit()
    db.refresh(response)
    return response


@router.post("/ctes/{cte_id}/trl-assessments/{level}/submit", status_code=status.HTTP_200_OK)
async def submit_for_approval(
    cte_id: int,
    level: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Submit TRL assessment for approval"""
    await check_cte_access(cte_id)(current_user=current_user, db=db)
    
    assessment = db.query(CTETRLAssessment).filter(
        CTETRLAssessment.cte_id == cte_id,
        CTETRLAssessment.trl_level == level
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TRL assessment not found"
        )
    
    assessment.status = AssessmentStatus.SUBMITTED
    db.commit()
    
    return {"message": "Assessment submitted for approval"}


@router.get("/ctes/{cte_id}/current-trl")
async def get_current_trl(
    cte_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get computed current TRL for CTE"""
    await check_cte_access(cte_id)(current_user=current_user, db=db)
    
    from app.core.trl_engine import compute_cte_trl
    current_trl = compute_cte_trl(db, cte_id)
    
    return {"cte_id": cte_id, "current_trl": current_trl}


@router.post("/ctes/{cte_id}/advance-trl", status_code=status.HTTP_200_OK)
async def advance_trl_level(
    cte_id: int,
    request_data: AdvanceTRLRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Advance CTE to target TRL level after completing all required questions"""
    await check_cte_access(cte_id)(current_user=current_user, db=db)
    
    target_level = request_data.target_level
    
    # Get TRL definition
    trl_def = db.query(TRLDefinition).filter(
        TRLDefinition.level == target_level,
        TRLDefinition.is_active == True
    ).first()
    
    if not trl_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TRL level {target_level} definition not found"
        )
    
    # Get or create assessment
    assessment = db.query(CTETRLAssessment).filter(
        CTETRLAssessment.cte_id == cte_id,
        CTETRLAssessment.trl_level == target_level
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assessment not found. Please submit responses first."
        )
    
    # Get all required questions
    required_questions = db.query(TRLQuestion).filter(
        TRLQuestion.trl_definition_id == trl_def.id,
        TRLQuestion.is_required == True
    ).all()
    
    # Check all required questions are answered
    for question in required_questions:
        response = db.query(TRLResponse).filter(
            TRLResponse.cte_trl_assessment_id == assessment.id,
            TRLResponse.trl_question_id == question.id
        ).first()
        
        if not response or not response.answer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Required question not answered: {question.question_text}"
            )
        
        # Check evidence if required
        if question.evidence_required:
            has_evidence = response.evidence_text or db.query(EvidenceItem).filter(
                EvidenceItem.trl_response_id == response.id
            ).first()
            
            if not has_evidence:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Evidence required for question: {question.question_text}"
                )
    
    # Evaluate IRL/MRL coupling against configured matrix
    required = get_coupling_requirement(db, target_level)
    current_irl = compute_cte_irl(db, cte_id)
    current_mrl = compute_cte_mrl(db, cte_id)
    cte = db.query(CTE).filter(CTE.id == cte_id).first()
    strict_mode = get_strict_mode_default(db)
    if cte:
        project_cfg = db.query(ProjectReadinessConfig).filter(ProjectReadinessConfig.project_id == cte.project_id).first()
        if project_cfg and project_cfg.strict_mode_override is not None:
            strict_mode = project_cfg.strict_mode_override

    coupling_ok = current_irl >= required["min_irl"] and current_mrl >= required["min_mrl"]
    if strict_mode and not coupling_ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Strict mode enabled. TRL {target_level} requires minimum IRL {required['min_irl']} "
                f"(current {current_irl}) and MRL {required['min_mrl']} (current {current_mrl})."
            )
        )

    # Mark assessment as approved (no approval workflow needed)
    from app.models.cte import AssessmentStatus
    assessment.status = AssessmentStatus.APPROVED
    
    db.commit()
    
    return {
        "message": f"Successfully advanced to TRL {target_level}",
        "current_trl": target_level,
        "coupling": {
            "strict_mode": strict_mode,
            "required_min_irl": required["min_irl"],
            "required_min_mrl": required["min_mrl"],
            "current_irl": current_irl,
            "current_mrl": current_mrl,
            "satisfied": coupling_ok,
        }
    }


@router.get("/ctes/{cte_id}/coupling-status/{target_level}")
async def get_trl_coupling_status(
    cte_id: int,
    target_level: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    await check_cte_access(cte_id)(current_user=current_user, db=db)
    required = get_coupling_requirement(db, target_level)
    current_irl = compute_cte_irl(db, cte_id)
    current_mrl = compute_cte_mrl(db, cte_id)
    cte = db.query(CTE).filter(CTE.id == cte_id).first()
    strict_mode = get_strict_mode_default(db)
    if cte:
        project_cfg = db.query(ProjectReadinessConfig).filter(ProjectReadinessConfig.project_id == cte.project_id).first()
        if project_cfg and project_cfg.strict_mode_override is not None:
            strict_mode = project_cfg.strict_mode_override
    return {
        "strict_mode": strict_mode,
        "required_min_irl": required["min_irl"],
        "required_min_mrl": required["min_mrl"],
        "current_irl": current_irl,
        "current_mrl": current_mrl,
        "satisfied": current_irl >= required["min_irl"] and current_mrl >= required["min_mrl"],
    }
