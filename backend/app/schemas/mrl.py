from __future__ import annotations

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.trl import TRLResponseAnswer
from app.models.cte import AssessmentStatus


class MRLQuestionResponse(BaseModel):
    id: int
    mrl_definition_id: int
    question_text: str
    question_order: int
    is_required: bool
    evidence_required: bool
    weight: float

    class Config:
        from_attributes = True


class MRLDefinitionResponse(BaseModel):
    id: int
    level: int
    name: str
    description: Optional[str] = None
    evidence_required: bool
    min_confidence: Optional[float] = None
    is_active: bool
    questions: List[MRLQuestionResponse] = []

    class Config:
        from_attributes = True


class MRLResponseCreate(BaseModel):
    mrl_question_id: int
    answer: TRLResponseAnswer
    evidence_text: Optional[str] = None
    confidence_score: Optional[float] = None


class MRLResponseResponse(BaseModel):
    id: int
    cte_mrl_assessment_id: int
    mrl_question_id: int
    answer: TRLResponseAnswer
    evidence_text: Optional[str] = None
    confidence_score: Optional[float] = None
    submitted_at: datetime

    class Config:
        from_attributes = True


class CTEMRLAssessmentCreate(BaseModel):
    mrl_level: int
    notes: Optional[str] = None
    confidence_score: Optional[float] = None


class CTEMRLAssessmentResponse(BaseModel):
    id: int
    cte_id: int
    mrl_level: int
    assessment_date: datetime
    assessed_by: int
    status: AssessmentStatus
    confidence_score: Optional[float] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class AdvanceMRLRequest(BaseModel):
    target_level: int
