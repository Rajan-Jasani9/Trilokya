from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import CTEIRLAssessment, IRLDefinition, IRLQuestion, IRLResponse
from app.schemas.irl import (
    CTEIRLAssessmentCreate,
    CTEIRLAssessmentResponse,
    IRLQuestionResponse,
    IRLResponseCreate,
    IRLResponseResponse,
    AdvanceIRLRequest,
)
from app.api.deps import get_current_active_user, check_cte_access
from app.models.cte import AssessmentStatus
from app.core.readiness_engine import compute_cte_irl

router = APIRouter()


@router.get("/ctes/{cte_id}/irl-assessments", response_model=List[CTEIRLAssessmentResponse])
async def list_irl_assessments(
    cte_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    await check_cte_access(cte_id)(current_user=current_user, db=db)
    return db.query(CTEIRLAssessment).filter(CTEIRLAssessment.cte_id == cte_id).all()


@router.post("/ctes/{cte_id}/irl-assessments/{level}", response_model=CTEIRLAssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_irl_assessment(
    cte_id: int,
    level: int,
    assessment_data: CTEIRLAssessmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    await check_cte_access(cte_id)(current_user=current_user, db=db)
    existing = db.query(CTEIRLAssessment).filter(CTEIRLAssessment.cte_id == cte_id, CTEIRLAssessment.irl_level == level).first()
    if existing:
        raise HTTPException(status_code=400, detail="IRL assessment for this level already exists")
    assessment = CTEIRLAssessment(
        cte_id=cte_id,
        irl_level=level,
        assessed_by=current_user.id,
        notes=assessment_data.notes,
        confidence_score=assessment_data.confidence_score,
        status=AssessmentStatus.DRAFT,
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@router.get("/ctes/{cte_id}/irl-assessments/{level}/questions", response_model=List[IRLQuestionResponse])
async def get_irl_questions(
    cte_id: int,
    level: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    await check_cte_access(cte_id)(current_user=current_user, db=db)
    definition = db.query(IRLDefinition).filter(IRLDefinition.level == level, IRLDefinition.is_active == True).first()
    if not definition:
        raise HTTPException(status_code=404, detail=f"IRL level {level} definition not found")
    return db.query(IRLQuestion).filter(IRLQuestion.irl_definition_id == definition.id).order_by(IRLQuestion.question_order).all()


@router.post("/ctes/{cte_id}/irl-assessments/{level}/responses", response_model=IRLResponseResponse, status_code=status.HTTP_201_CREATED)
async def submit_irl_response(
    cte_id: int,
    level: int,
    response_data: IRLResponseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    await check_cte_access(cte_id)(current_user=current_user, db=db)
    assessment = db.query(CTEIRLAssessment).filter(CTEIRLAssessment.cte_id == cte_id, CTEIRLAssessment.irl_level == level).first()
    if not assessment:
        assessment = CTEIRLAssessment(cte_id=cte_id, irl_level=level, assessed_by=current_user.id, status=AssessmentStatus.DRAFT)
        db.add(assessment)
        db.flush()
    existing = db.query(IRLResponse).filter(
        IRLResponse.cte_irl_assessment_id == assessment.id,
        IRLResponse.irl_question_id == response_data.irl_question_id
    ).first()
    if existing:
        existing.answer = response_data.answer
        existing.evidence_text = response_data.evidence_text
        existing.confidence_score = response_data.confidence_score
        response = existing
    else:
        response = IRLResponse(
            cte_irl_assessment_id=assessment.id,
            irl_question_id=response_data.irl_question_id,
            answer=response_data.answer,
            evidence_text=response_data.evidence_text,
            confidence_score=response_data.confidence_score
        )
        db.add(response)
    db.commit()
    db.refresh(response)
    return response


@router.post("/ctes/{cte_id}/irl-assessments/{level}/submit", status_code=200)
async def submit_irl_for_approval(
    cte_id: int,
    level: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    await check_cte_access(cte_id)(current_user=current_user, db=db)
    assessment = db.query(CTEIRLAssessment).filter(CTEIRLAssessment.cte_id == cte_id, CTEIRLAssessment.irl_level == level).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="IRL assessment not found")
    assessment.status = AssessmentStatus.SUBMITTED
    db.commit()
    return {"message": "Assessment submitted for approval"}


@router.get("/ctes/{cte_id}/current-irl")
async def get_current_irl(
    cte_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    await check_cte_access(cte_id)(current_user=current_user, db=db)
    return {"cte_id": cte_id, "current_irl": compute_cte_irl(db, cte_id)}


@router.post("/ctes/{cte_id}/advance-irl", status_code=200)
async def advance_irl_level(
    cte_id: int,
    request_data: AdvanceIRLRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    await check_cte_access(cte_id)(current_user=current_user, db=db)
    target_level = request_data.target_level
    definition = db.query(IRLDefinition).filter(IRLDefinition.level == target_level, IRLDefinition.is_active == True).first()
    if not definition:
        raise HTTPException(status_code=404, detail=f"IRL level {target_level} definition not found")
    assessment = db.query(CTEIRLAssessment).filter(CTEIRLAssessment.cte_id == cte_id, CTEIRLAssessment.irl_level == target_level).first()
    if not assessment:
        raise HTTPException(status_code=400, detail="Assessment not found. Please submit responses first.")
    required_questions = db.query(IRLQuestion).filter(IRLQuestion.irl_definition_id == definition.id, IRLQuestion.is_required == True).all()
    for question in required_questions:
        response = db.query(IRLResponse).filter(
            IRLResponse.cte_irl_assessment_id == assessment.id,
            IRLResponse.irl_question_id == question.id
        ).first()
        if not response or not response.answer:
            raise HTTPException(status_code=400, detail=f"Required question not answered: {question.question_text}")
        if question.evidence_required and not response.evidence_text:
            raise HTTPException(status_code=400, detail=f"Evidence required for question: {question.question_text}")
    assessment.status = AssessmentStatus.APPROVED
    db.commit()
    return {"message": f"Successfully advanced to IRL {target_level}", "current_irl": target_level}
