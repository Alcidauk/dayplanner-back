from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class UserAvailabilityCreate(BaseModel):
    starting_hour: str
    ending_hour: datetime
    available_days: dict
    user_id: Optional[int] = None


class UserAvailabilityResponse(UserAvailabilityCreate):
    id: int

    model_config = {
        "from_attributes": True
    }