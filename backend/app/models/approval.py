from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Approval(Base):
    __tablename__ = "approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    cte_trl_assessment_id = Column(Integer, ForeignKey("cte_trl_assessments.id", ondelete="CASCADE"), nullable=False)
    approver_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    approval_level = Column(Integer, nullable=False)  # Order in workflow (1, 2, 3...)
    status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False)
    comments = Column(Text, nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    assessment = relationship("CTETRLAssessment", back_populates="approvals")
    approver = relationship("User", back_populates="approvals", foreign_keys=[approver_id])


class WorkflowConfig(Base):
    __tablename__ = "workflow_config"
    
    id = Column(Integer, primary_key=True, index=True)
    approval_level = Column(Integer, unique=True, nullable=False)
    role_required = Column(String, nullable=False)  # Role name (e.g., "Assistant Manager", "Manager")
    is_mandatory = Column(Boolean, default=True)
    order_sequence = Column(Integer, nullable=False)  # Order in workflow
    
    class Config:
        unique_together = [("approval_level", "order_sequence")]
