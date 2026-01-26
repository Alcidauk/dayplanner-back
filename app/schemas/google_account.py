from pydantic import BaseModel
from typing import Optional


class GoogleAccountCreate(BaseModel):
    google_sub: str
    email: str
    user_id: Optional[int] = None
    token_id: Optional[int] = None


class GoogleAccountResponse(GoogleAccountCreate):
    id: int

    model_config = {
        "from_attributes": True
    }