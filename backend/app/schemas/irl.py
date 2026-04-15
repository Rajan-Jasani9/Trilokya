from __future__ import annotations

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.trl import TRLResponseAnswer
from app.models.cte import AssessmentStatus


class IRLQuestionResponse(BaseModel):
    id: int
    irl_definition_id: int
    question_text: str
    question_order: int
    is_required: bool
    evidence_required: bool
    weight: float

    class Config:
        from_attributes = True


class IRLDefinitionResponse(BaseModel):
    id: int
    level: int
    name: str
    description: Optional[str] = None
    evidence_required: bool
    min_confidence: Optional[float] = None
    is_active: bool
    questions: List[IRLQuestionResponse] = []

    class Config:
        from_attributes = True


class IRLResponseCreate(BaseModel):
    irl_question_id: int
    answer: TRLResponseAnswer
    evidence_text: Optional[str] = None
    confidence_score: Optional[float] = None


class IRLResponseResponse(BaseModel):
    id: int
    cte_irl_assessment_id: int
    irl_question_id: int
    answer: TRLResponseAnswer
    evidence_text: Optional[str] = None
    confidence_score: Optional[float] = None
    submitted_at: datetime

    class Config:
        from_attributes = True


class CTEIRLAssessmentCreate(BaseModel):
    irl_level: int
    notes: Optional[str] = None
    confidence_score: Optional[float] = None


class CTEIRLAssessmentResponse(BaseModel):
    id: int
    cte_id: int
    irl_level: int
    assessment_date: datetime
    assessed_by: int
    status: AssessmentStatus
    confidence_score: Optional[float] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class AdvanceIRLRequest(BaseModel):
    target_level: int
