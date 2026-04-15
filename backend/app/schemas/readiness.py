from pydantic import BaseModel
from typing import Optional, List


class TRLCouplingConfigItem(BaseModel):
    trl_level: int
    min_irl: int
    min_mrl: int

    class Config:
        from_attributes = True


class TRLCouplingConfigUpdate(BaseModel):
    items: List[TRLCouplingConfigItem]


class ReadinessSettingsResponse(BaseModel):
    strict_mode_default: bool


class ReadinessSettingsUpdate(BaseModel):
    strict_mode_default: bool


class ProjectReadinessConfigUpdate(BaseModel):
    strict_mode_override: Optional[bool] = None
