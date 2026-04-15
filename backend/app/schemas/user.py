from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class RoleResponse(BaseModel):
    id: int
    name: str
    hierarchy_level: int
    permissions_json: dict
    
    class Config:
        from_attributes = True


class OrgUnitResponse(BaseModel):
    id: int
    code: str
    name: str
    parent_id: Optional[int] = None
    org_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrgUnitCreate(BaseModel):
    code: str
    name: str
    parent_id: Optional[int] = None
    org_type: str


class OrgUnitUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    parent_id: Optional[int] = None
    org_type: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    org_units: List[OrgUnitResponse] = []
    roles: List[RoleResponse] = []
    
    class Config:
        from_attributes = True
