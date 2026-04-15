from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.database import get_db
from app.models import (
    TRLDefinition,
    TRLQuestion,
    IRLDefinition,
    IRLQuestion,
    MRLDefinition,
    MRLQuestion,
    WorkflowConfig,
    OrgUnit,
    TRLCouplingConfig,
    ReadinessSettings,
    ProjectReadinessConfig,
    UserOrgUnit,
    UserRole,
    ProjectOrgUnit,
)
from app.schemas.trl import TRLDefinitionResponse, TRLQuestionResponse
from app.schemas.irl import IRLDefinitionResponse, IRLQuestionResponse
from app.schemas.mrl import MRLDefinitionResponse, MRLQuestionResponse
from app.schemas.readiness import (
    TRLCouplingConfigUpdate,
    TRLCouplingConfigItem,
    ReadinessSettingsResponse,
    ReadinessSettingsUpdate,
    ProjectReadinessConfigUpdate,
)
from app.schemas.approval import WorkflowConfigResponse
from app.schemas.user import OrgUnitResponse, OrgUnitCreate, OrgUnitUpdate
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


@router.get("/irl-definitions", response_model=List[IRLDefinitionResponse])
async def list_irl_definitions(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("SuperAdmin"))
):
    return db.query(IRLDefinition).filter(IRLDefinition.is_active == True).order_by(IRLDefinition.level).all()


@router.get("/mrl-definitions", response_model=List[MRLDefinitionResponse])
async def list_mrl_definitions(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("SuperAdmin"))
):
    return db.query(MRLDefinition).filter(MRLDefinition.is_active == True).order_by(MRLDefinition.level).all()


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


@router.post("/irl-definitions", response_model=IRLDefinitionResponse, status_code=status.HTTP_201_CREATED)
async def create_irl_definition(
    definition_data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("SuperAdmin"))
):
    existing = db.query(IRLDefinition).filter(IRLDefinition.level == definition_data["level"]).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"IRL level {definition_data['level']} already exists")
    definition = IRLDefinition(
        level=definition_data["level"],
        name=definition_data["name"],
        description=definition_data.get("description"),
        evidence_required=definition_data.get("evidence_required", True),
        min_confidence=definition_data.get("min_confidence"),
        is_active=definition_data.get("is_active", True),
    )
    db.add(definition)
    db.commit()
    db.refresh(definition)
    return definition


@router.patch("/irl-definitions/{def_id}", response_model=IRLDefinitionResponse)
async def update_irl_definition(
    def_id: int,
    definition_data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("SuperAdmin"))
):
    definition = db.query(IRLDefinition).filter(IRLDefinition.id == def_id).first()
    if not definition:
        raise HTTPException(status_code=404, detail="IRL definition not found")
    for field, value in {k: v for k, v in definition_data.items() if v is not None}.items():
        if field != "level":
            setattr(definition, field, value)
    db.commit()
    db.refresh(definition)
    return definition


@router.delete("/irl-definitions/{def_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_irl_definition(
    def_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("SuperAdmin"))
):
    definition = db.query(IRLDefinition).filter(IRLDefinition.id == def_id).first()
    if not definition:
        raise HTTPException(status_code=404, detail="IRL definition not found")
    db.delete(definition)
    db.commit()
    return None


@router.post("/irl-questions", response_model=IRLQuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_irl_question(
    question_data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("SuperAdmin"))
):
    definition = db.query(IRLDefinition).filter(IRLDefinition.id == question_data["irl_definition_id"]).first()
    if not definition:
        raise HTTPException(status_code=404, detail="IRL definition not found")
    question = IRLQuestion(
        irl_definition_id=question_data["irl_definition_id"],
        question_text=question_data["question_text"],
        question_order=question_data.get("question_order", 1),
        is_required=question_data.get("is_required", True),
        evidence_required=question_data.get("evidence_required", True),
        weight=question_data.get("weight", 1.0),
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


@router.patch("/irl-questions/{question_id}", response_model=IRLQuestionResponse)
async def update_irl_question(
    question_id: int,
    question_data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("SuperAdmin"))
):
    question = db.query(IRLQuestion).filter(IRLQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="IRL question not found")
    for field, value in {k: v for k, v in question_data.items() if v is not None}.items():
        if field != "irl_definition_id":
            setattr(question, field, value)
    db.commit()
    db.refresh(question)
    return question


@router.delete("/irl-questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_irl_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("SuperAdmin"))
):
    question = db.query(IRLQuestion).filter(IRLQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="IRL question not found")
    db.delete(question)
    db.commit()
    return None


@router.post("/mrl-definitions", response_model=MRLDefinitionResponse, status_code=status.HTTP_201_CREATED)
async def create_mrl_definition(
    definition_data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("SuperAdmin"))
):
    existing = db.query(MRLDefinition).filter(MRLDefinition.level == definition_data["level"]).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"MRL level {definition_data['level']} already exists")
    definition = MRLDefinition(
        level=definition_data["level"],
        name=definition_data["name"],
        description=definition_data.get("description"),
        evidence_required=definition_data.get("evidence_required", True),
        min_confidence=definition_data.get("min_confidence"),
        is_active=definition_data.get("is_active", True),
    )
    db.add(definition)
    db.commit()
    db.refresh(definition)
    return definition


@router.patch("/mrl-definitions/{def_id}", response_model=MRLDefinitionResponse)
async def update_mrl_definition(
    def_id: int,
    definition_data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("SuperAdmin"))
):
    definition = db.query(MRLDefinition).filter(MRLDefinition.id == def_id).first()
    if not definition:
        raise HTTPException(status_code=404, detail="MRL definition not found")
    for field, value in {k: v for k, v in definition_data.items() if v is not None}.items():
        if field != "level":
            setattr(definition, field, value)
    db.commit()
    db.refresh(definition)
    return definition


@router.delete("/mrl-definitions/{def_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mrl_definition(
    def_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("SuperAdmin"))
):
    definition = db.query(MRLDefinition).filter(MRLDefinition.id == def_id).first()
    if not definition:
        raise HTTPException(status_code=404, detail="MRL definition not found")
    db.delete(definition)
    db.commit()
    return None


@router.post("/mrl-questions", response_model=MRLQuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_mrl_question(
    question_data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("SuperAdmin"))
):
    definition = db.query(MRLDefinition).filter(MRLDefinition.id == question_data["mrl_definition_id"]).first()
    if not definition:
        raise HTTPException(status_code=404, detail="MRL definition not found")
    question = MRLQuestion(
        mrl_definition_id=question_data["mrl_definition_id"],
        question_text=question_data["question_text"],
        question_order=question_data.get("question_order", 1),
        is_required=question_data.get("is_required", True),
        evidence_required=question_data.get("evidence_required", True),
        weight=question_data.get("weight", 1.0),
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


@router.patch("/mrl-questions/{question_id}", response_model=MRLQuestionResponse)
async def update_mrl_question(
    question_id: int,
    question_data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("SuperAdmin"))
):
    question = db.query(MRLQuestion).filter(MRLQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="MRL question not found")
    for field, value in {k: v for k, v in question_data.items() if v is not None}.items():
        if field != "mrl_definition_id":
            setattr(question, field, value)
    db.commit()
    db.refresh(question)
    return question


@router.delete("/mrl-questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mrl_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("SuperAdmin"))
):
    question = db.query(MRLQuestion).filter(MRLQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="MRL question not found")
    db.delete(question)
    db.commit()
    return None


@router.get("/trl-coupling-config", response_model=List[TRLCouplingConfigItem])
async def get_trl_coupling_config(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("SuperAdmin"))
):
    return db.query(TRLCouplingConfig).order_by(TRLCouplingConfig.trl_level).all()


@router.put("/trl-coupling-config", response_model=List[TRLCouplingConfigItem])
async def update_trl_coupling_config(
    payload: TRLCouplingConfigUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("SuperAdmin"))
):
    db.query(TRLCouplingConfig).delete()
    for item in payload.items:
        db.add(TRLCouplingConfig(trl_level=item.trl_level, min_irl=item.min_irl, min_mrl=item.min_mrl))
    db.commit()
    return db.query(TRLCouplingConfig).order_by(TRLCouplingConfig.trl_level).all()


@router.get("/readiness-settings", response_model=ReadinessSettingsResponse)
async def get_readiness_settings(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("SuperAdmin"))
):
    settings = db.query(ReadinessSettings).first()
    if not settings:
        settings = ReadinessSettings(strict_mode_default=False)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return {"strict_mode_default": settings.strict_mode_default}


@router.put("/readiness-settings", response_model=ReadinessSettingsResponse)
async def update_readiness_settings(
    payload: ReadinessSettingsUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("SuperAdmin"))
):
    settings = db.query(ReadinessSettings).first()
    if not settings:
        settings = ReadinessSettings(strict_mode_default=payload.strict_mode_default)
        db.add(settings)
    else:
        settings.strict_mode_default = payload.strict_mode_default
    db.commit()
    db.refresh(settings)
    return {"strict_mode_default": settings.strict_mode_default}


@router.put("/projects/{project_id}/readiness-config")
async def set_project_readiness_config(
    project_id: int,
    payload: ProjectReadinessConfigUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("SuperAdmin"))
):
    config = db.query(ProjectReadinessConfig).filter(ProjectReadinessConfig.project_id == project_id).first()
    if not config:
        config = ProjectReadinessConfig(project_id=project_id, strict_mode_override=payload.strict_mode_override)
        db.add(config)
    else:
        config.strict_mode_override = payload.strict_mode_override
    db.commit()
    return {"project_id": project_id, "strict_mode_override": config.strict_mode_override}


@router.get("/org-units", response_model=List[OrgUnitResponse])
async def list_org_units(
    db: Session = Depends(get_db),
    current_user = Depends(require_role("SuperAdmin"))
):
    """List all org units (SuperAdmin only)"""
    return db.query(OrgUnit).order_by(OrgUnit.name).all()


@router.post("/org-units", response_model=OrgUnitResponse, status_code=status.HTTP_201_CREATED)
async def create_org_unit(
    payload: OrgUnitCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("SuperAdmin"))
):
    """Create organization unit (SuperAdmin only)"""
    if db.query(OrgUnit).filter(OrgUnit.code == payload.code).first():
        raise HTTPException(status_code=400, detail="Org unit code already exists")

    if payload.parent_id is not None:
        parent = db.query(OrgUnit).filter(OrgUnit.id == payload.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent org unit not found")

    org_unit = OrgUnit(
        code=payload.code.strip(),
        name=payload.name.strip(),
        parent_id=payload.parent_id,
        org_type=payload.org_type.strip(),
    )
    db.add(org_unit)
    db.commit()
    db.refresh(org_unit)
    return org_unit


@router.patch("/org-units/{org_unit_id}", response_model=OrgUnitResponse)
async def update_org_unit(
    org_unit_id: int,
    payload: OrgUnitUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("SuperAdmin"))
):
    """Update organization unit (SuperAdmin only)"""
    org_unit = db.query(OrgUnit).filter(OrgUnit.id == org_unit_id).first()
    if not org_unit:
        raise HTTPException(status_code=404, detail="Org unit not found")

    update_data = payload.dict(exclude_unset=True)

    if "code" in update_data and update_data["code"] is not None:
        new_code = update_data["code"].strip()
        exists = db.query(OrgUnit).filter(OrgUnit.code == new_code, OrgUnit.id != org_unit_id).first()
        if exists:
            raise HTTPException(status_code=400, detail="Org unit code already exists")
        org_unit.code = new_code

    if "name" in update_data and update_data["name"] is not None:
        org_unit.name = update_data["name"].strip()

    if "org_type" in update_data and update_data["org_type"] is not None:
        org_unit.org_type = update_data["org_type"].strip()

    if "parent_id" in update_data:
        parent_id = update_data["parent_id"]
        if parent_id == org_unit_id:
            raise HTTPException(status_code=400, detail="Org unit cannot be its own parent")
        if parent_id is not None:
            parent = db.query(OrgUnit).filter(OrgUnit.id == parent_id).first()
            if not parent:
                raise HTTPException(status_code=404, detail="Parent org unit not found")
        org_unit.parent_id = parent_id

    db.commit()
    db.refresh(org_unit)
    return org_unit


@router.delete("/org-units/{org_unit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_org_unit(
    org_unit_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("SuperAdmin"))
):
    """Delete organization unit (SuperAdmin only)"""
    org_unit = db.query(OrgUnit).filter(OrgUnit.id == org_unit_id).first()
    if not org_unit:
        raise HTTPException(status_code=404, detail="Org unit not found")

    has_children = db.query(OrgUnit).filter(OrgUnit.parent_id == org_unit_id).first()
    if has_children:
        raise HTTPException(status_code=400, detail="Cannot delete org unit with child units")

    is_used = (
        db.query(UserOrgUnit).filter(UserOrgUnit.org_unit_id == org_unit_id).first()
        or db.query(UserRole).filter(UserRole.org_unit_id == org_unit_id).first()
        or db.query(ProjectOrgUnit).filter(ProjectOrgUnit.org_unit_id == org_unit_id).first()
    )
    if is_used:
        raise HTTPException(status_code=400, detail="Cannot delete org unit that is in use")

    db.delete(org_unit)
    db.commit()
    return None
