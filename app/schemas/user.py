from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    surname: str
    email: str
    password: str
    google_account_id: Optional[int] = None


class UserResponse(UserCreate):
    id: int

    model_config = {
        "from_attributes": True
    }


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    user: dict
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    user: dict
    token_type: str = "bearer"
