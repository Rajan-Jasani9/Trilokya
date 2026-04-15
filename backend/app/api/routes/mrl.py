from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import CTEMRLAssessment, MRLDefinition, MRLQuestion, MRLResponse
from app.schemas.mrl import (
    CTEMRLAssessmentCreate,
    CTEMRLAssessmentResponse,
    MRLQuestionResponse,
    MRLResponseCreate,
    MRLResponseResponse,
    AdvanceMRLRequest,
)
from app.api.deps import get_current_active_user, check_cte_access
from app.models.cte import AssessmentStatus
from app.core.readiness_engine import compute_cte_mrl

router = APIRouter()


@router.get("/ctes/{cte_id}/mrl-assessments", response_model=List[CTEMRLAssessmentResponse])
async def list_mrl_assessments(
    cte_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    await check_cte_access(cte_id)(current_user=current_user, db=db)
    return db.query(CTEMRLAssessment).filter(CTEMRLAssessment.cte_id == cte_id).all()


@router.post("/ctes/{cte_id}/mrl-assessments/{level}", response_model=CTEMRLAssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_mrl_assessment(
    cte_id: int,
    level: int,
    assessment_data: CTEMRLAssessmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    await check_cte_access(cte_id)(current_user=current_user, db=db)
    existing = db.query(CTEMRLAssessment).filter(CTEMRLAssessment.cte_id == cte_id, CTEMRLAssessment.mrl_level == level).first()
    if existing:
        raise HTTPException(status_code=400, detail="MRL assessment for this level already exists")
    assessment = CTEMRLAssessment(
        cte_id=cte_id,
        mrl_level=level,
        assessed_by=current_user.id,
        notes=assessment_data.notes,
        confidence_score=assessment_data.confidence_score,
        status=AssessmentStatus.DRAFT,
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@router.get("/ctes/{cte_id}/mrl-assessments/{level}/questions", response_model=List[MRLQuestionResponse])
async def get_mrl_questions(
    cte_id: int,
    level: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    await check_cte_access(cte_id)(current_user=current_user, db=db)
    definition = db.query(MRLDefinition).filter(MRLDefinition.level == level, MRLDefinition.is_active == True).first()
    if not definition:
        raise HTTPException(status_code=404, detail=f"MRL level {level} definition not found")
    return db.query(MRLQuestion).filter(MRLQuestion.mrl_definition_id == definition.id).order_by(MRLQuestion.question_order).all()


@router.post("/ctes/{cte_id}/mrl-assessments/{level}/responses", response_model=MRLResponseResponse, status_code=status.HTTP_201_CREATED)
async def submit_mrl_response(
    cte_id: int,
    level: int,
    response_data: MRLResponseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    await check_cte_access(cte_id)(current_user=current_user, db=db)
    assessment = db.query(CTEMRLAssessment).filter(CTEMRLAssessment.cte_id == cte_id, CTEMRLAssessment.mrl_level == level).first()
    if not assessment:
        assessment = CTEMRLAssessment(cte_id=cte_id, mrl_level=level, assessed_by=current_user.id, status=AssessmentStatus.DRAFT)
        db.add(assessment)
        db.flush()
    existing = db.query(MRLResponse).filter(
        MRLResponse.cte_mrl_assessment_id == assessment.id,
        MRLResponse.mrl_question_id == response_data.mrl_question_id
    ).first()
    if existing:
        existing.answer = response_data.answer
        existing.evidence_text = response_data.evidence_text
        existing.confidence_score = response_data.confidence_score
        response = existing
    else:
        response = MRLResponse(
            cte_mrl_assessment_id=assessment.id,
            mrl_question_id=response_data.mrl_question_id,
            answer=response_data.answer,
            evidence_text=response_data.evidence_text,
            confidence_score=response_data.confidence_score
        )
        db.add(response)
    db.commit()
    db.refresh(response)
    return response


@router.post("/ctes/{cte_id}/mrl-assessments/{level}/submit", status_code=200)
async def submit_mrl_for_approval(
    cte_id: int,
    level: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    await check_cte_access(cte_id)(current_user=current_user, db=db)
    assessment = db.query(CTEMRLAssessment).filter(CTEMRLAssessment.cte_id == cte_id, CTEMRLAssessment.mrl_level == level).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="MRL assessment not found")
    assessment.status = AssessmentStatus.SUBMITTED
    db.commit()
    return {"message": "Assessment submitted for approval"}


@router.get("/ctes/{cte_id}/current-mrl")
async def get_current_mrl(
    cte_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    await check_cte_access(cte_id)(current_user=current_user, db=db)
    return {"cte_id": cte_id, "current_mrl": compute_cte_mrl(db, cte_id)}


@router.post("/ctes/{cte_id}/advance-mrl", status_code=200)
async def advance_mrl_level(
    cte_id: int,
    request_data: AdvanceMRLRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    await check_cte_access(cte_id)(current_user=current_user, db=db)
    target_level = request_data.target_level
    definition = db.query(MRLDefinition).filter(MRLDefinition.level == target_level, MRLDefinition.is_active == True).first()
    if not definition:
        raise HTTPException(status_code=404, detail=f"MRL level {target_level} definition not found")
    assessment = db.query(CTEMRLAssessment).filter(CTEMRLAssessment.cte_id == cte_id, CTEMRLAssessment.mrl_level == target_level).first()
    if not assessment:
        raise HTTPException(status_code=400, detail="Assessment not found. Please submit responses first.")
    required_questions = db.query(MRLQuestion).filter(MRLQuestion.mrl_definition_id == definition.id, MRLQuestion.is_required == True).all()
    for question in required_questions:
        response = db.query(MRLResponse).filter(
            MRLResponse.cte_mrl_assessment_id == assessment.id,
            MRLResponse.mrl_question_id == question.id
        ).first()
        if not response or not response.answer:
            raise HTTPException(status_code=400, detail=f"Required question not answered: {question.question_text}")
        if question.evidence_required and not response.evidence_text:
            raise HTTPException(status_code=400, detail=f"Evidence required for question: {question.question_text}")
    assessment.status = AssessmentStatus.APPROVED
    db.commit()
    return {"message": f"Successfully advanced to MRL {target_level}", "current_mrl": target_level}
