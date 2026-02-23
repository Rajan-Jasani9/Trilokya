from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class AssessmentStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


class CTE(Base):
    __tablename__ = "ctes"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True)
    target_trl = Column(Integer, nullable=True)  # Target TRL milestone for this CTE
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="ctes")
    trl_assessments = relationship("CTETRLAssessment", back_populates="cte", cascade="all, delete-orphan")
    irl_assessments = relationship("CTEIRLAssessment", back_populates="cte", cascade="all, delete-orphan")
    mrl_assessments = relationship("CTEMRLAssessment", back_populates="cte", cascade="all, delete-orphan")
    srl_assessments = relationship("CTESRLAssessment", back_populates="cte", cascade="all, delete-orphan")


class CTETRLAssessment(Base):
    __tablename__ = "cte_trl_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    cte_id = Column(Integer, ForeignKey("ctes.id", ondelete="CASCADE"), nullable=False)
    trl_level = Column(Integer, nullable=False)
    assessment_date = Column(DateTime(timezone=True), server_default=func.now())
    assessed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    status = Column(SQLEnum(AssessmentStatus), default=AssessmentStatus.DRAFT, nullable=False)
    confidence_score = Column(Float, nullable=True)  # 0-1 or aggregated
    notes = Column(Text, nullable=True)
    
    # Relationships
    cte = relationship("CTE", back_populates="trl_assessments")
    assessor = relationship("User", back_populates="trl_assessments", foreign_keys=[assessed_by])
    responses = relationship("TRLResponse", back_populates="assessment", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="assessment", cascade="all, delete-orphan")


class CTEIRLAssessment(Base):
    __tablename__ = "cte_irl_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    cte_id = Column(Integer, ForeignKey("ctes.id", ondelete="CASCADE"), nullable=False)
    irl_level = Column(Integer, nullable=False)
    assessment_date = Column(DateTime(timezone=True), server_default=func.now())
    assessed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    status = Column(SQLEnum(AssessmentStatus), default=AssessmentStatus.DRAFT, nullable=False)
    confidence_score = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    cte = relationship("CTE", back_populates="irl_assessments")


class CTEMRLAssessment(Base):
    __tablename__ = "cte_mrl_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    cte_id = Column(Integer, ForeignKey("ctes.id", ondelete="CASCADE"), nullable=False)
    mrl_level = Column(Integer, nullable=False)
    assessment_date = Column(DateTime(timezone=True), server_default=func.now())
    assessed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    status = Column(SQLEnum(AssessmentStatus), default=AssessmentStatus.DRAFT, nullable=False)
    confidence_score = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    cte = relationship("CTE", back_populates="mrl_assessments")


class CTESRLAssessment(Base):
    __tablename__ = "cte_srl_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    cte_id = Column(Integer, ForeignKey("ctes.id", ondelete="CASCADE"), nullable=False)
    srl_level = Column(Integer, nullable=False)
    assessment_date = Column(DateTime(timezone=True), server_default=func.now())
    assessed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    status = Column(SQLEnum(AssessmentStatus), default=AssessmentStatus.DRAFT, nullable=False)
    confidence_score = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    cte = relationship("CTE", back_populates="srl_assessments")
