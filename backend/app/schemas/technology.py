from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TechnologyBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon_filename: Optional[str] = None
    is_active: bool = True
    display_order: int = 0


class TechnologyCreate(TechnologyBase):
    pass


class TechnologyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon_filename: Optional[str] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None


class TechnologyResponse(TechnologyBase):
    id: int
    created_at: datetime
    project_count: int = 0
    icon_url: Optional[str] = None

    class Config:
        from_attributes = True
