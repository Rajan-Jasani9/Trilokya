from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action_type = Column(String, nullable=False)  # e.g., "TRL_CHANGE", "EVIDENCE_UPLOAD", "APPROVAL", "ROLE_CHANGE", "OVERRIDE"
    entity_type = Column(String, nullable=False)  # e.g., "Project", "CTE", "TRLAssessment"
    entity_id = Column(Integer, nullable=True)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
