from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.approval import ApprovalStatus


class ApprovalCreate(BaseModel):
    comments: Optional[str] = None


class ApprovalResponse(BaseModel):
    id: int
    cte_trl_assessment_id: int
    approver_id: int
    approval_level: int
    status: ApprovalStatus
    comments: Optional[str] = None
    approved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class WorkflowConfigResponse(BaseModel):
    id: int
    approval_level: int
    role_required: str
    is_mandatory: bool
    order_sequence: int
    
    class Config:
        from_attributes = True
