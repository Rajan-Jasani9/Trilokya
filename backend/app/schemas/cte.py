from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.cte import AssessmentStatus


class CTEBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    target_trl: Optional[int] = None


class CTECreate(CTEBase):
    project_id: int


class CTEUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    target_trl: Optional[int] = None


class CTETRLAssessmentCreate(BaseModel):
    trl_level: int
    notes: Optional[str] = None
    confidence_score: Optional[float] = None


class CTETRLAssessmentResponse(BaseModel):
    id: int
    cte_id: int
    trl_level: int
    assessment_date: datetime
    assessed_by: int
    status: AssessmentStatus
    confidence_score: Optional[float] = None
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class CTEResponse(CTEBase):
    id: int
    project_id: int
    created_at: datetime
    trl_assessments: List[CTETRLAssessmentResponse] = []
    
    class Config:
        from_attributes = True
