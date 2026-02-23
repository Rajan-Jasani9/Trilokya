from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.database import get_db
from app.models import TRLDefinition, TRLQuestion, WorkflowConfig, OrgUnit
from app.schemas.trl import TRLDefinitionResponse, TRLQuestionResponse
from app.schemas.approval import WorkflowConfigResponse
from app.api.deps import require_role
from app.utils.excel_loader import load_trl_definitions_from_excel

router = APIRouter()


@router.get("/trl-definitions", response_model=List[TRLDefinitionResponse])
async def list_trl_definitions(
    db: Session = Depends(get_db),
    current_user = Depends(require_role("SuperAdmin"))
):
    """List all TRL definitions (SuperAdmin only)"""
    definitions = db.query(TRLDefinition).filter(TRLDefinition.is_active == True).order_by(TRLDefinition.level).all()
    return definitions


@router.post("/trl-definitions/upload", status_code=status.HTTP_201_CREATED)
async def upload_trl_definitions(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_role("SuperAdmin"))
):
    """Upload TRL definitions from Excel (SuperAdmin only)"""
    import tempfile
    import os
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Load definitions from Excel
        definitions = load_trl_definitions_from_excel(tmp_path)
        
        # Save to database
        for def_data in definitions:
            trl_def = db.query(TRLDefinition).filter(TRLDefinition.level == def_data["level"]).first()
            
            if trl_def:
                # Update existing
                trl_def.name = def_data["name"]
                trl_def.description = def_data.get("description")
                # Evidence required by default unless explicitly disabled in config
                trl_def.evidence_required = def_data.get("evidence_required", True)
                trl_def.min_confidence = def_data.get("min_confidence")
            else:
                # Create new
                trl_def = TRLDefinition(
                    level=def_data["level"],
                    name=def_data["name"],
                    description=def_data.get("description"),
                    # Default: evidence required unless explicitly configured otherwise
                    evidence_required=def_data.get("evidence_required", True),
                    min_confidence=def_data.get("min_confidence")
                )
                db.add(trl_def)
                db.flush()
            
            # Handle questions
            for q_data in def_data.get("questions", []):
                question = db.query(TRLQuestion).filter(
                    TRLQuestion.trl_definition_id == trl_def.id,
                    TRLQuestion.question_order == q_data["order"]
                ).first()
                
                if question:
                    question.question_text = q_data["text"]
                    question.is_required = q_data.get("is_required", True)
                    question.evidence_required = q_data.get("evidence_required", False)
                    question.weight = q_data.get("weight", 1.0)
                else:
                    question = TRLQuestion(
                        trl_definition_id=trl_def.id,
                        question_text=q_data["text"],
                        question_order=q_data["order"],
                        is_required=q_data.get("is_required", True),
                        evidence_required=q_data.get("evidence_required", False),
                        weight=q_data.get("weight", 1.0)
                    )
                    db.add(question)
        
        db.commit()
        return {"message": "TRL definitions uploaded successfully"}
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.get("/workflow-config", response_model=List[WorkflowConfigResponse])
async def get_workflow_config(
    db: Session = Depends(get_db),
    current_user = Depends(require_role("SuperAdmin"))
):
    """Get workflow configuration (SuperAdmin only)"""
    configs = db.query(WorkflowConfig).order_by(WorkflowConfig.order_sequence).all()
    return configs


@router.post("/workflow-config", response_model=WorkflowConfigResponse, status_code=status.HTTP_201_CREATED)
async def update_workflow_config(
    config_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("SuperAdmin"))
):
    """Update workflow configuration (SuperAdmin only)"""
    # This is a simplified version - in production, handle full config update
    config = WorkflowConfig(
        approval_level=config_data["approval_level"],
        role_required=config_data["role_required"],
        is_mandatory=config_data.get("is_mandatory", True),
        order_sequence=config_data["order_sequence"]
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


@router.post("/trl-definitions", response_model=TRLDefinitionResponse, status_code=status.HTTP_201_CREATED)
async def create_trl_definition(
    definition_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("SuperAdmin"))
):
    """Create a new TRL definition (SuperAdmin only)"""
    # Check if level already exists
    existing = db.query(TRLDefinition).filter(TRLDefinition.level == definition_data["level"]).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"TRL level {definition_data['level']} already exists"
        )
    
    trl_def = TRLDefinition(
        level=definition_data["level"],
        name=definition_data["name"],
        description=definition_data.get("description"),
        # Evidence required by default; admin can turn it off explicitly
        evidence_required=definition_data.get("evidence_required", True),
        min_confidence=definition_data.get("min_confidence"),
        is_active=definition_data.get("is_active", True)
    )
    db.add(trl_def)
    db.commit()
    db.refresh(trl_def)
    return trl_def


@router.patch("/trl-definitions/{def_id}", response_model=TRLDefinitionResponse)
async def update_trl_definition(
    def_id: int,
    definition_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("SuperAdmin"))
):
    """Update TRL definition (SuperAdmin only)"""
    trl_def = db.query(TRLDefinition).filter(TRLDefinition.id == def_id).first()
    if not trl_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TRL definition not found"
        )
    
    update_data = {k: v for k, v in definition_data.items() if v is not None}
    
    for field, value in update_data.items():
        if field != "level":  # Level is immutable
            setattr(trl_def, field, value)
    
    db.commit()
    db.refresh(trl_def)
    return trl_def


@router.delete("/trl-definitions/{def_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trl_definition(
    def_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("SuperAdmin"))
):
    """Delete TRL definition (SuperAdmin only)"""
    trl_def = db.query(TRLDefinition).filter(TRLDefinition.id == def_id).first()
    if not trl_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TRL definition not found"
        )
    
    db.delete(trl_def)
    db.commit()
    return None


@router.post("/trl-questions", response_model=TRLQuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_trl_question(
    question_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("SuperAdmin"))
):
    """Create a new TRL question (SuperAdmin only)"""
    trl_def = db.query(TRLDefinition).filter(TRLDefinition.id == question_data["trl_definition_id"]).first()
    if not trl_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TRL definition not found"
        )
    
    question = TRLQuestion(
        trl_definition_id=question_data["trl_definition_id"],
        question_text=question_data["question_text"],
        question_order=question_data.get("question_order", 1),
        is_required=question_data.get("is_required", True),
        # Evidence required by default unless explicitly disabled
        evidence_required=question_data.get("evidence_required", True),
        weight=question_data.get("weight", 1.0)
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


@router.patch("/trl-questions/{question_id}", response_model=TRLQuestionResponse)
async def update_trl_question(
    question_id: int,
    question_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("SuperAdmin"))
):
    """Update TRL question (SuperAdmin only)"""
    question = db.query(TRLQuestion).filter(TRLQuestion.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TRL question not found"
        )
    
    update_data = {k: v for k, v in question_data.items() if v is not None}
    
    for field, value in update_data.items():
        if field != "trl_definition_id":  # Definition ID is immutable
            setattr(question, field, value)
    
    db.commit()
    db.refresh(question)
    return question


@router.delete("/trl-questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trl_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("SuperAdmin"))
):
    """Delete TRL question (SuperAdmin only)"""
    question = db.query(TRLQuestion).filter(TRLQuestion.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TRL question not found"
        )
    
    db.delete(question)
    db.commit()
    return None


@router.get("/org-units", response_model=List[dict])
async def list_org_units(
    db: Session = Depends(get_db),
    current_user = Depends(require_role("SuperAdmin"))
):
    """List all org units (SuperAdmin only)"""
    org_units = db.query(OrgUnit).all()
    return [
        {
            "id": ou.id,
            "code": ou.code,
            "name": ou.name,
            "parent_id": ou.parent_id,
            "org_type": ou.org_type
        }
        for ou in org_units
    ]
