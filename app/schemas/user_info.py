from typing import Optional
from pydantic import BaseModel


class UserInfoCreate(BaseModel):
    place: str
    interests: list[str]


class UserInfoResponse(UserInfoCreate):
    id: int

    model_config = {
        "from_attributes": True
    }
