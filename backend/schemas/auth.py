from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"

    model_config = ConfigDict(extra="forbid")


class TokenPayload(BaseModel):
    sub: str
    exp: int
    type: str

    model_config = ConfigDict(extra="forbid")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(extra="forbid")


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=8)

    model_config = ConfigDict(extra="forbid")


class RefreshRequest(BaseModel):
    refresh_token: str

    model_config = ConfigDict(extra="forbid")
