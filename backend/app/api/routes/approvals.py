from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Approval, CTETRLAssessment, WorkflowConfig
from app.schemas.approval import ApprovalCreate, ApprovalResponse
from app.api.deps import get_current_active_user, require_minimum_role_level
from app.models.approval import ApprovalStatus
from app.core.permissions import get_user_roles

router = APIRouter()


@router.get("/pending", response_model=List[ApprovalResponse])
async def list_pending_approvals(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List pending approvals for current user"""
    user_roles = get_user_roles(db, current_user.id)
    
    # Get workflow configs for user's roles
    workflow_configs = db.query(WorkflowConfig).filter(
        WorkflowConfig.role_required.in_(user_roles)
    ).all()
    
    approval_levels = [wc.approval_level for wc in workflow_configs]
    
    # Get pending approvals
    approvals = db.query(Approval).filter(
        Approval.status == ApprovalStatus.PENDING,
        Approval.approval_level.in_(approval_levels)
    ).all()
    
    return approvals


@router.post("/{approval_id}/approve", response_model=ApprovalResponse)
async def approve_assessment(
    approval_id: int,
    approval_data: ApprovalCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Approve a TRL assessment"""
    approval = db.query(Approval).filter(Approval.id == approval_id).first()
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found"
        )
    
    if approval.status != ApprovalStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approval is not pending"
        )
    
    # Check if user has required role
    user_roles = get_user_roles(db, current_user.id)
    workflow_config = db.query(WorkflowConfig).filter(
        WorkflowConfig.approval_level == approval.approval_level
    ).first()
    
    if not workflow_config or workflow_config.role_required not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have required role for this approval level"
        )
    
    from datetime import datetime
    approval.status = ApprovalStatus.APPROVED
    approval.comments = approval_data.comments
    approval.approved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(approval)
    
    # Check if all required approvals are done, update assessment status
    assessment = db.query(CTETRLAssessment).filter(
        CTETRLAssessment.id == approval.cte_trl_assessment_id
    ).first()
    
    if assessment:
        # Check if all mandatory approvals are done
        mandatory_configs = db.query(WorkflowConfig).filter(
            WorkflowConfig.is_mandatory == True
        ).all()
        
        approved_levels = db.query(Approval.approval_level).filter(
            Approval.cte_trl_assessment_id == assessment.id,
            Approval.status == ApprovalStatus.APPROVED
        ).all()
        approved_levels = [al[0] for al in approved_levels]
        
        all_approved = all(
            mc.approval_level in approved_levels
            for mc in mandatory_configs
        )
        
        if all_approved:
            assessment.status = AssessmentStatus.APPROVED
    
    db.commit()
    
    return approval


@router.post("/{approval_id}/reject", response_model=ApprovalResponse)
async def reject_assessment(
    approval_id: int,
    approval_data: ApprovalCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Reject a TRL assessment"""
    approval = db.query(Approval).filter(Approval.id == approval_id).first()
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found"
        )
    
    if approval.status != ApprovalStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approval is not pending"
        )
    
    # Check if user has required role
    user_roles = get_user_roles(db, current_user.id)
    workflow_config = db.query(WorkflowConfig).filter(
        WorkflowConfig.approval_level == approval.approval_level
    ).first()
    
    if not workflow_config or workflow_config.role_required not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have required role for this approval level"
        )
    
    from datetime import datetime
    approval.status = ApprovalStatus.REJECTED
    approval.comments = approval_data.comments
    approval.approved_at = datetime.utcnow()
    
    # Reject assessment
    assessment = db.query(CTETRLAssessment).filter(
        CTETRLAssessment.id == approval.cte_trl_assessment_id
    ).first()
    if assessment:
        assessment.status = AssessmentStatus.REJECTED
    
    db.commit()
    db.refresh(approval)
    
    return approval
