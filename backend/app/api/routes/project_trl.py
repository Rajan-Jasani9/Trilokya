from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db
from app.models import Project, ProjectTRLAssessment, ProjectTRLResponse, ProjectEvidenceItem, TRLDefinition, TRLQuestion
from app.schemas.project_trl import (
    ProjectTRLAssessmentCreate, ProjectTRLAssessmentResponse,
    ProjectTRLResponseCreate, ProjectTRLResponseResponse,
    ProjectAdvanceTRLRequest, ProjectEvidenceItemResponse
)
from app.schemas.trl import TRLQuestionResponse
from app.api.deps import get_current_active_user, check_project_access
from app.models.cte import AssessmentStatus
from app.models.trl import TRLResponseAnswer

router = APIRouter()


@router.get("/projects/{project_id}/trl-assessments", response_model=List[ProjectTRLAssessmentResponse])
async def list_project_trl_assessments(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List TRL assessments for a project"""
    await check_project_access(project_id)(current_user=current_user, db=db)
    
    assessments = db.query(ProjectTRLAssessment).filter(
        ProjectTRLAssessment.project_id == project_id
    ).options(
        joinedload(ProjectTRLAssessment.responses).joinedload(ProjectTRLResponse.question),
        joinedload(ProjectTRLAssessment.responses).joinedload(ProjectTRLResponse.evidence_items)
    ).order_by(ProjectTRLAssessment.trl_level.desc()).all()
    
    return assessments


@router.get("/projects/{project_id}/current-trl")
async def get_project_current_trl(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get computed current TRL for project"""
    await check_project_access(project_id)(current_user=current_user, db=db)
    
    from app.core.trl_engine import compute_project_trl
    current_trl = compute_project_trl(db, project_id)
    
    # Also check for project-level assessments
    highest_assessment = db.query(ProjectTRLAssessment).filter(
        ProjectTRLAssessment.project_id == project_id,
        ProjectTRLAssessment.status == AssessmentStatus.APPROVED
    ).order_by(ProjectTRLAssessment.trl_level.desc()).first()
    
    project_trl = highest_assessment.trl_level if highest_assessment else 0
    
    # Return the higher of computed (from CTEs) or project assessment
    return {
        "project_id": project_id,
        "current_trl": max(current_trl, project_trl)
    }


@router.get("/projects/{project_id}/trl-assessments/{level}/questions", response_model=List[TRLQuestionResponse])
async def get_project_trl_questions(
    project_id: int,
    level: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get questions for a TRL level for project assessment"""
    await check_project_access(project_id)(current_user=current_user, db=db)
    
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


@router.post("/projects/{project_id}/trl-assessments/{level}", response_model=ProjectTRLAssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_project_trl_assessment(
    project_id: int,
    level: int,
    assessment_data: ProjectTRLAssessmentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Start a new TRL assessment for a project"""
    await check_project_access(project_id)(current_user=current_user, db=db)
    
    # Check if assessment already exists
    existing = db.query(ProjectTRLAssessment).filter(
        ProjectTRLAssessment.project_id == project_id,
        ProjectTRLAssessment.trl_level == level
    ).first()
    
    if existing:
        # Return existing assessment
        db.refresh(existing)
        return existing
    
    assessment = ProjectTRLAssessment(
        project_id=project_id,
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


@router.post("/projects/{project_id}/trl-assessments/{level}/responses", response_model=ProjectTRLResponseResponse, status_code=status.HTTP_201_CREATED)
async def submit_project_trl_response(
    project_id: int,
    level: int,
    response_data: ProjectTRLResponseCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Submit or update a TRL response for project"""
    await check_project_access(project_id)(current_user=current_user, db=db)
    
    # Get or create assessment
    assessment = db.query(ProjectTRLAssessment).filter(
        ProjectTRLAssessment.project_id == project_id,
        ProjectTRLAssessment.trl_level == level
    ).first()
    
    if not assessment:
        assessment = ProjectTRLAssessment(
            project_id=project_id,
            trl_level=level,
            assessed_by=current_user.id,
            status=AssessmentStatus.DRAFT
        )
        db.add(assessment)
        db.flush()
    
    # Check if response already exists
    existing = db.query(ProjectTRLResponse).filter(
        ProjectTRLResponse.project_trl_assessment_id == assessment.id,
        ProjectTRLResponse.trl_question_id == response_data.trl_question_id
    ).first()
    
    if existing:
        # Update existing response
        existing.answer = response_data.answer
        existing.evidence_text = response_data.evidence_text
        existing.confidence_score = response_data.confidence_score
        response = existing
    else:
        # Create new response
        response = ProjectTRLResponse(
            project_trl_assessment_id=assessment.id,
            trl_question_id=response_data.trl_question_id,
            answer=response_data.answer,
            evidence_text=response_data.evidence_text,
            confidence_score=response_data.confidence_score
        )
        db.add(response)
        db.flush()
    
    db.commit()
    db.refresh(response)
    
    # Load relationships
    response = db.query(ProjectTRLResponse).filter(ProjectTRLResponse.id == response.id).options(
        joinedload(ProjectTRLResponse.question),
        joinedload(ProjectTRLResponse.evidence_items)
    ).first()
    
    return response


@router.post("/projects/{project_id}/advance-trl", status_code=status.HTTP_200_OK)
async def advance_project_trl_level(
    project_id: int,
    request_data: ProjectAdvanceTRLRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Advance project to target TRL level after completing all required questions"""
    await check_project_access(project_id)(current_user=current_user, db=db)
    
    target_level = request_data.target_level
    if not target_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="target_level is required"
        )
    
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
    assessment = db.query(ProjectTRLAssessment).filter(
        ProjectTRLAssessment.project_id == project_id,
        ProjectTRLAssessment.trl_level == target_level
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
        response = db.query(ProjectTRLResponse).filter(
            ProjectTRLResponse.project_trl_assessment_id == assessment.id,
            ProjectTRLResponse.trl_question_id == question.id
        ).first()
        
        if not response or not response.answer or response.answer == TRLResponseAnswer.NA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Required question not answered or marked 'Not Applicable': {question.question_text}"
            )
        
        # Check evidence if required
        if question.evidence_required:
            has_evidence = response.evidence_text or db.query(ProjectEvidenceItem).filter(
                ProjectEvidenceItem.project_trl_response_id == response.id
            ).first()
            
            if not has_evidence:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Evidence required for question: {question.question_text}"
                )
    
    # Mark assessment as approved
    assessment.status = AssessmentStatus.APPROVED
    assessment.notes = request_data.notes
    
    db.commit()
    
    return {
        "message": f"Successfully advanced to TRL {target_level}",
        "new_trl_level": target_level
    }


@router.post("/projects/{project_id}/evidence/upload")
async def upload_project_evidence(
    project_id: int,
    file: UploadFile = File(...),
    project_trl_response_id: int = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Upload evidence file for project TRL response"""
    await check_project_access(project_id)(current_user=current_user, db=db)
    
    if not project_trl_response_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="project_trl_response_id is required"
        )
    
    # Verify response exists and belongs to this project
    response = db.query(ProjectTRLResponse).join(ProjectTRLAssessment).filter(
        ProjectTRLResponse.id == project_trl_response_id,
        ProjectTRLAssessment.project_id == project_id
    ).first()
    
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TRL response not found"
        )
    
    # Save file (simplified - in production, use proper file storage)
    import os
    from pathlib import Path
    
    upload_dir = Path("uploads/project_evidence")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / f"{project_trl_response_id}_{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    evidence_item = ProjectEvidenceItem(
        project_trl_response_id=project_trl_response_id,
        evidence_type="upload",
        file_path=str(file_path),
        file_name=file.filename,
        file_size=len(content),
        uploaded_by=current_user.id
    )
    db.add(evidence_item)
    db.commit()
    db.refresh(evidence_item)
    
    return evidence_item


@router.post("/projects/{project_id}/evidence/link")
async def add_project_evidence_link(
    project_id: int,
    evidence_data: dict,
    project_trl_response_id: int = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Add external link as evidence for project TRL response"""
    await check_project_access(project_id)(current_user=current_user, db=db)
    
    if not project_trl_response_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="project_trl_response_id is required"
        )
    
    # Verify response exists
    response = db.query(ProjectTRLResponse).join(ProjectTRLAssessment).filter(
        ProjectTRLResponse.id == project_trl_response_id,
        ProjectTRLAssessment.project_id == project_id
    ).first()
    
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TRL response not found"
        )
    
    evidence_item = ProjectEvidenceItem(
        project_trl_response_id=project_trl_response_id,
        evidence_type="link",
        external_url=evidence_data.get("external_url"),
        file_name=evidence_data.get("file_name", evidence_data.get("external_url")),
        uploaded_by=current_user.id
    )
    db.add(evidence_item)
    db.commit()
    db.refresh(evidence_item)
    
    return evidence_item
