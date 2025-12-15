from typing import Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    surname: str
    email: str
    google_account_id: Optional[int] = None


class UserResponse(UserCreate):
    id: int

    model_config = {
        "from_attributes": True
    }