from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models.cte import AssessmentStatus
from app.models.trl import TRLResponseAnswer, EvidenceType


class ProjectTRLAssessment(Base):
    """TRL Assessment at Project Level"""
    __tablename__ = "project_trl_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    trl_level = Column(Integer, nullable=False)
    assessment_date = Column(DateTime(timezone=True), server_default=func.now())
    assessed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    status = Column(SQLEnum(AssessmentStatus), default=AssessmentStatus.DRAFT, nullable=False)
    confidence_score = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="trl_assessments")
    assessor = relationship("User", foreign_keys=[assessed_by])
    responses = relationship("ProjectTRLResponse", back_populates="assessment", cascade="all, delete-orphan")


class ProjectTRLResponse(Base):
    """TRL Response for Project-level assessments"""
    __tablename__ = "project_trl_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    project_trl_assessment_id = Column(Integer, ForeignKey("project_trl_assessments.id", ondelete="CASCADE"), nullable=False)
    trl_question_id = Column(Integer, ForeignKey("trl_questions.id", ondelete="CASCADE"), nullable=False)
    answer = Column(SQLEnum(TRLResponseAnswer), nullable=False)
    evidence_text = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    assessment = relationship("ProjectTRLAssessment", back_populates="responses")
    question = relationship("TRLQuestion")
    evidence_items = relationship("ProjectEvidenceItem", back_populates="response", cascade="all, delete-orphan")


class ProjectEvidenceItem(Base):
    """Evidence items for project TRL responses"""
    __tablename__ = "project_evidence_items"
    
    id = Column(Integer, primary_key=True, index=True)
    project_trl_response_id = Column(Integer, ForeignKey("project_trl_responses.id", ondelete="CASCADE"), nullable=False)
    evidence_type = Column(SQLEnum(EvidenceType), nullable=False)
    file_path = Column(String, nullable=True)  # For uploaded files
    external_url = Column(String, nullable=True)  # For external links
    file_name = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)  # Bytes
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    response = relationship("ProjectTRLResponse", back_populates="evidence_items")
    uploader = relationship("User", foreign_keys=[uploaded_by])
