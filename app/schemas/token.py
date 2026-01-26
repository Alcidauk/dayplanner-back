from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TokenCreate(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_expiry: Optional[datetime] = None
    user_id: Optional[int] = None
    google_account_id: Optional[int] = None


class TokenResponse(TokenCreate):
    id: int

    model_config = {
        "from_attributes": True
    }
