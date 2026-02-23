from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class OrgUnit(Base):
    __tablename__ = "org_units"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("org_units.id", ondelete="SET NULL"), nullable=True)
    org_type = Column(String, nullable=False)  # Lab, Division, Directorate
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    parent = relationship("OrgUnit", remote_side=[id], backref="children")
    users = relationship("UserOrgUnit", back_populates="org_unit")
    user_roles = relationship("UserRole", back_populates="org_unit")
    projects = relationship("ProjectOrgUnit", back_populates="org_unit")


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    org_units = relationship("UserOrgUnit", back_populates="user", cascade="all, delete-orphan")
    roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    created_projects = relationship("Project", back_populates="creator", foreign_keys="Project.created_by")
    project_memberships = relationship("ProjectMember", back_populates="user", cascade="all, delete-orphan")
    trl_assessments = relationship("CTETRLAssessment", back_populates="assessor")
    approvals = relationship("Approval", back_populates="approver")
    audit_logs = relationship("AuditLog", back_populates="user")


class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # SuperAdmin, Manager, Assistant Manager, Engineer, Scientist
    hierarchy_level = Column(Integer, nullable=False)  # 5=SuperAdmin, 4=Manager, 3=Assistant Manager, 2=Engineer/Scientist
    permissions_json = Column(JSON, default={})  # Configurable permissions
    
    # Relationships
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")


class UserOrgUnit(Base):
    __tablename__ = "user_org_units"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    org_unit_id = Column(Integer, ForeignKey("org_units.id", ondelete="CASCADE"), primary_key=True)
    
    # Relationships
    user = relationship("User", back_populates="org_units")
    org_unit = relationship("OrgUnit", back_populates="users")


class UserRole(Base):
    __tablename__ = "user_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    org_unit_id = Column(Integer, ForeignKey("org_units.id", ondelete="CASCADE"), nullable=True)  # Context-specific role
    
    # Relationships
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="user_roles")
    org_unit = relationship("OrgUnit", back_populates="user_roles")
