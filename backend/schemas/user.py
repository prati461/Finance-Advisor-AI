from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    risk_profile: Optional[str] = Field(None, max_length=32)
    investment_horizon_years: Optional[int] = Field(None, ge=1, le=100)

    model_config = ConfigDict(extra="forbid")


class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    risk_profile: Optional[str] = None
    investment_horizon_years: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

    model_config = ConfigDict(extra="forbid")
