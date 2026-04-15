from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models.trl import TRLResponseAnswer
from app.models.cte import AssessmentStatus


class IRLDefinition(Base):
    __tablename__ = "irl_definitions"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    evidence_required = Column(Boolean, default=True)
    min_confidence = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)

    questions = relationship(
        "IRLQuestion",
        back_populates="irl_definition",
        cascade="all, delete-orphan",
        order_by="IRLQuestion.question_order",
    )


class IRLQuestion(Base):
    __tablename__ = "irl_questions"

    id = Column(Integer, primary_key=True, index=True)
    irl_definition_id = Column(Integer, ForeignKey("irl_definitions.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_order = Column(Integer, nullable=False)
    is_required = Column(Boolean, default=True)
    evidence_required = Column(Boolean, default=True)
    weight = Column(Float, default=1.0)

    irl_definition = relationship("IRLDefinition", back_populates="questions")
    responses = relationship("IRLResponse", back_populates="question", cascade="all, delete-orphan")


class IRLResponse(Base):
    __tablename__ = "irl_responses"

    id = Column(Integer, primary_key=True, index=True)
    cte_irl_assessment_id = Column(Integer, ForeignKey("cte_irl_assessments.id", ondelete="CASCADE"), nullable=False)
    irl_question_id = Column(Integer, ForeignKey("irl_questions.id", ondelete="CASCADE"), nullable=False)
    answer = Column(SQLEnum(TRLResponseAnswer), nullable=False)
    evidence_text = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    assessment = relationship("CTEIRLAssessment", back_populates="responses")
    question = relationship("IRLQuestion", back_populates="responses")


class MRLDefinition(Base):
    __tablename__ = "mrl_definitions"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    evidence_required = Column(Boolean, default=True)
    min_confidence = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)

    questions = relationship(
        "MRLQuestion",
        back_populates="mrl_definition",
        cascade="all, delete-orphan",
        order_by="MRLQuestion.question_order",
    )


class MRLQuestion(Base):
    __tablename__ = "mrl_questions"

    id = Column(Integer, primary_key=True, index=True)
    mrl_definition_id = Column(Integer, ForeignKey("mrl_definitions.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_order = Column(Integer, nullable=False)
    is_required = Column(Boolean, default=True)
    evidence_required = Column(Boolean, default=True)
    weight = Column(Float, default=1.0)

    mrl_definition = relationship("MRLDefinition", back_populates="questions")
    responses = relationship("MRLResponse", back_populates="question", cascade="all, delete-orphan")


class MRLResponse(Base):
    __tablename__ = "mrl_responses"

    id = Column(Integer, primary_key=True, index=True)
    cte_mrl_assessment_id = Column(Integer, ForeignKey("cte_mrl_assessments.id", ondelete="CASCADE"), nullable=False)
    mrl_question_id = Column(Integer, ForeignKey("mrl_questions.id", ondelete="CASCADE"), nullable=False)
    answer = Column(SQLEnum(TRLResponseAnswer), nullable=False)
    evidence_text = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    assessment = relationship("CTEMRLAssessment", back_populates="responses")
    question = relationship("MRLQuestion", back_populates="responses")


class TRLCouplingConfig(Base):
    __tablename__ = "trl_coupling_config"

    id = Column(Integer, primary_key=True, index=True)
    trl_level = Column(Integer, unique=True, nullable=False, index=True)
    min_irl = Column(Integer, nullable=False)
    min_mrl = Column(Integer, nullable=False)


class ReadinessSettings(Base):
    __tablename__ = "readiness_settings"

    id = Column(Integer, primary_key=True, index=True)
    strict_mode_default = Column(Boolean, nullable=False, default=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ProjectReadinessConfig(Base):
    __tablename__ = "project_readiness_config"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True)
    strict_mode_override = Column(Boolean, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="readiness_config")
