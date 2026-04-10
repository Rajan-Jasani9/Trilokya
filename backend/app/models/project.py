from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class ProjectCategory(str, enum.Enum):
    HARDWARE = "Hardware"
    SOFTWARE = "Software"
    AI = "AI"
    MIXED = "Mixed"


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False, index=True)  # Immutable
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(SQLEnum(ProjectCategory), nullable=False)
    target_trl = Column(Integer, nullable=True)  # Target TRL milestone
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="created_projects", foreign_keys=[created_by])
    org_units = relationship("ProjectOrgUnit", back_populates="project", cascade="all, delete-orphan")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    ctes = relationship("CTE", back_populates="project", cascade="all, delete-orphan")
    trl_overrides = relationship("ProjectTRLOverride", back_populates="project", cascade="all, delete-orphan")
    trl_assessments = relationship("ProjectTRLAssessment", back_populates="project", cascade="all, delete-orphan")
    technologies = relationship("ProjectTechnology", back_populates="project", cascade="all, delete-orphan")


class ProjectOrgUnit(Base):
    __tablename__ = "project_org_units"
    
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    org_unit_id = Column(Integer, ForeignKey("org_units.id", ondelete="CASCADE"), primary_key=True)
    
    # Relationships
    project = relationship("Project", back_populates="org_units")
    org_unit = relationship("OrgUnit", back_populates="projects")


class ProjectMember(Base):
    __tablename__ = "project_members"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_in_project = Column(String, nullable=True)  # Optional project-specific role
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_memberships")


class ProjectTechnology(Base):
    __tablename__ = "project_technologies"

    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    technology_id = Column(Integer, ForeignKey("technologies.id", ondelete="CASCADE"), primary_key=True)

    # Relationships
    project = relationship("Project", back_populates="technologies")
    technology = relationship("Technology", back_populates="projects")


class ProjectTRLOverride(Base):
    __tablename__ = "project_trl_overrides"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    trl_value = Column(Integer, nullable=False)
    overridden_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="trl_overrides")
    overrider = relationship("User", foreign_keys=[overridden_by])
