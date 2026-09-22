from typing import Literal, Optional
from pydantic import BaseModel, EmailStr


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    role: Literal["DONOR", "CAMPAIGNER"]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    role: str
    phone: Optional[str] = None
    access_token: str
    token_type: str = "bearer"