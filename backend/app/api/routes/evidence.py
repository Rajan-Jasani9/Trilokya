from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from pathlib import Path
from app.database import get_db
from app.models import EvidenceItem, TRLResponse, User
from app.schemas.trl import EvidenceItemCreate, EvidenceItemResponse
from app.api.deps import get_current_active_user
from app.config import settings
from app.core.file_storage import save_uploaded_file, validate_file_type, validate_file_size

router = APIRouter()


@router.post("/upload", response_model=EvidenceItemResponse, status_code=status.HTTP_201_CREATED)
async def upload_evidence(
    trl_response_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload evidence file"""
    # Verify TRL response exists
    response = db.query(TRLResponse).filter(TRLResponse.id == trl_response_id).first()
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TRL response not found"
        )
    
    # Validate file
    file_ext = Path(file.filename).suffix[1:].lower() if file.filename else ""
    if not validate_file_type(file_ext):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.allowed_file_types_list)}"
        )
    
    # Validate file size
    file_content = await file.read()
    if not validate_file_size(len(file_content)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB"
        )
    
    # Save file
    file_path = save_uploaded_file(
        file_content,
        file.filename,
        response.cte_trl_assessment_id,
        trl_response_id
    )
    
    # Create evidence item
    evidence = EvidenceItem(
        trl_response_id=trl_response_id,
        evidence_type="upload",
        file_path=file_path,
        file_name=file.filename,
        file_size=len(file_content),
        uploaded_by=current_user.id
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    
    return evidence


@router.post("/link", response_model=EvidenceItemResponse, status_code=status.HTTP_201_CREATED)
async def add_evidence_link(
    trl_response_id: int,
    evidence_data: EvidenceItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add external evidence link"""
    if evidence_data.evidence_type != "link":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Evidence type must be 'link'"
        )
    
    # Verify TRL response exists
    response = db.query(TRLResponse).filter(TRLResponse.id == trl_response_id).first()
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TRL response not found"
        )
    
    evidence = EvidenceItem(
        trl_response_id=trl_response_id,
        evidence_type=evidence_data.evidence_type,
        external_url=evidence_data.external_url,
        file_name=evidence_data.file_name,
        uploaded_by=current_user.id
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    
    return evidence


@router.get("/{evidence_id}/download")
async def download_evidence(
    evidence_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Download evidence file"""
    from fastapi.responses import FileResponse
    
    evidence = db.query(EvidenceItem).filter(EvidenceItem.id == evidence_id).first()
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found"
        )
    
    if evidence.evidence_type != "upload" or not evidence.file_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Evidence is not a file upload"
        )
    
    full_path = os.path.join(settings.UPLOAD_DIR, evidence.file_path)
    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server"
        )
    
    return FileResponse(
        full_path,
        filename=evidence.file_name or "evidence",
        media_type="application/octet-stream"
    )


@router.delete("/{evidence_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evidence(
    evidence_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete evidence"""
    evidence = db.query(EvidenceItem).filter(EvidenceItem.id == evidence_id).first()
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found"
        )
    
    # Delete file if it's an upload
    if evidence.evidence_type == "upload" and evidence.file_path:
        full_path = os.path.join(settings.UPLOAD_DIR, evidence.file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
    
    db.delete(evidence)
    db.commit()
    return None
