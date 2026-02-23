from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from app.models.project import ProjectCategory


class ProjectBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    category: ProjectCategory
    target_trl: Optional[int] = None
    start_date: date
    end_date: Optional[date] = None


class ProjectCreate(ProjectBase):
    org_unit_ids: List[int] = []


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[ProjectCategory] = None
    # target_trl is computed from CTEs (min of all CTE target TRLs), not directly updatable
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    org_unit_ids: Optional[List[int]] = None


class ProjectMemberCreate(BaseModel):
    user_id: int
    role_in_project: Optional[str] = None


class ProjectTRLOverrideCreate(BaseModel):
    trl_value: int
    reason: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: int
    created_by: int
    created_at: datetime
    org_unit_ids: List[int] = []
    current_trl: Optional[int] = None
    trl_overrides: Optional[List[dict]] = None
    members: Optional[List[dict]] = None
    
    class Config:
        from_attributes = True
