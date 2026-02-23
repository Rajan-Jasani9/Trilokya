from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.cte import AssessmentStatus
from app.models.trl import TRLResponseAnswer, EvidenceType


class ProjectTRLAssessmentCreate(BaseModel):
    trl_level: int
    notes: Optional[str] = None
    confidence_score: Optional[float] = None


class ProjectTRLAssessmentResponse(BaseModel):
    id: int
    project_id: int
    trl_level: int
    assessment_date: datetime
    assessed_by: int
    status: AssessmentStatus
    confidence_score: Optional[float] = None
    notes: Optional[str] = None
    responses: List["ProjectTRLResponseResponse"] = []
    
    class Config:
        from_attributes = True


class ProjectEvidenceItemCreate(BaseModel):
    evidence_type: EvidenceType
    external_url: Optional[str] = None
    file_name: Optional[str] = None


class ProjectEvidenceItemResponse(BaseModel):
    id: int
    project_trl_response_id: int
    evidence_type: EvidenceType
    file_path: Optional[str] = None
    external_url: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    uploaded_by: int
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class ProjectTRLResponseCreate(BaseModel):
    trl_question_id: int
    answer: TRLResponseAnswer
    evidence_text: Optional[str] = None
    confidence_score: Optional[float] = None


class ProjectTRLResponseResponse(BaseModel):
    id: int
    project_trl_assessment_id: int
    trl_question_id: int
    answer: TRLResponseAnswer
    evidence_text: Optional[str] = None
    confidence_score: Optional[float] = None
    submitted_at: datetime
    question: Optional["TRLQuestionResponse"] = None
    evidence_items: List[ProjectEvidenceItemResponse] = []
    
    class Config:
        from_attributes = True


class ProjectAdvanceTRLRequest(BaseModel):
    target_level: int
    notes: Optional[str] = None
