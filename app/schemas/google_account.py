from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class GoogleAccountCreate(BaseModel):
    google_sub: str
    email: str
    access_token: str
    refresh_token: Optional[str] = None
    token_expiry: Optional[datetime] = None
    user_id: Optional[int] = None


class GoogleAccountResponse(GoogleAccountCreate):
    id: int

    model_config = {
        "from_attributes": True
    }