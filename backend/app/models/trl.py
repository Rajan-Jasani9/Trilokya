from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class TRLResponseAnswer(str, enum.Enum):
    YES = "Yes"
    NO = "No"
    NA = "Not Applicable"


class EvidenceType(str, enum.Enum):
    UPLOAD = "upload"
    LINK = "link"


class TRLDefinition(Base):
    __tablename__ = "trl_definitions"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    evidence_required = Column(Boolean, default=False)
    min_confidence = Column(Float, nullable=True)  # Minimum confidence threshold
    is_active = Column(Boolean, default=True)
    
    # Relationships
    questions = relationship("TRLQuestion", back_populates="trl_definition", cascade="all, delete-orphan", order_by="TRLQuestion.question_order")


class TRLQuestion(Base):
    __tablename__ = "trl_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    trl_definition_id = Column(Integer, ForeignKey("trl_definitions.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_order = Column(Integer, nullable=False)
    is_required = Column(Boolean, default=True)
    # By default, evidence is required for all questions unless explicitly disabled by admin
    evidence_required = Column(Boolean, default=True)
    weight = Column(Float, default=1.0)  # For weighted scoring
    
    # Relationships
    trl_definition = relationship("TRLDefinition", back_populates="questions")
    responses = relationship("TRLResponse", back_populates="question", cascade="all, delete-orphan")


class TRLResponse(Base):
    __tablename__ = "trl_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    cte_trl_assessment_id = Column(Integer, ForeignKey("cte_trl_assessments.id", ondelete="CASCADE"), nullable=False)
    trl_question_id = Column(Integer, ForeignKey("trl_questions.id", ondelete="CASCADE"), nullable=False)
    answer = Column(SQLEnum(TRLResponseAnswer), nullable=False)
    evidence_text = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)  # 0-1 or Low/Medium/High mapped to numbers
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    assessment = relationship("CTETRLAssessment", back_populates="responses")
    question = relationship("TRLQuestion", back_populates="responses")
    evidence_items = relationship("EvidenceItem", back_populates="response", cascade="all, delete-orphan")


class EvidenceItem(Base):
    __tablename__ = "evidence_items"
    
    id = Column(Integer, primary_key=True, index=True)
    trl_response_id = Column(Integer, ForeignKey("trl_responses.id", ondelete="CASCADE"), nullable=False)
    evidence_type = Column(SQLEnum(EvidenceType), nullable=False)
    file_path = Column(String, nullable=True)  # If upload
    external_url = Column(String, nullable=True)  # If link
    file_name = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)  # Bytes
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    response = relationship("TRLResponse", back_populates="evidence_items")
    uploader = relationship("User", foreign_keys=[uploaded_by])
