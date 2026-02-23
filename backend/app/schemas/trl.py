from __future__ import annotations

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.trl import TRLResponseAnswer, EvidenceType


class TRLQuestionResponse(BaseModel):
    id: int
    trl_definition_id: int
    question_text: str
    question_order: int
    is_required: bool
    evidence_required: bool
    weight: float
    
    class Config:
        from_attributes = True


class TRLDefinitionResponse(BaseModel):
    id: int
    level: int
    name: str
    description: Optional[str] = None
    evidence_required: bool
    min_confidence: Optional[float] = None
    is_active: bool
    questions: List[TRLQuestionResponse] = []
    
    class Config:
        from_attributes = True


class EvidenceItemCreate(BaseModel):
    evidence_type: EvidenceType
    external_url: Optional[str] = None
    file_name: Optional[str] = None


class EvidenceItemResponse(BaseModel):
    id: int
    trl_response_id: int
    evidence_type: EvidenceType
    file_path: Optional[str] = None
    external_url: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    uploaded_by: int
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class TRLResponseCreate(BaseModel):
    trl_question_id: int
    answer: TRLResponseAnswer
    evidence_text: Optional[str] = None
    confidence_score: Optional[float] = None
    evidence_items: List[EvidenceItemCreate] = []


class TRLResponseResponse(BaseModel):
    id: int
    cte_trl_assessment_id: int
    trl_question_id: int
    answer: TRLResponseAnswer
    evidence_text: Optional[str] = None
    confidence_score: Optional[float] = None
    submitted_at: datetime
    evidence_items: List[EvidenceItemResponse] = []
    
    class Config:
        from_attributes = True


class AdvanceTRLRequest(BaseModel):
    target_level: int
