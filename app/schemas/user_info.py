from typing import Optional
from pydantic import BaseModel


class UserInfoCreate(BaseModel):
    place: str
    interest: dict
    user_id: Optional[int] = None


class UserInfoResponse(UserInfoCreate):
    id: int

    model_config = {
        "from_attributes": True
    }
