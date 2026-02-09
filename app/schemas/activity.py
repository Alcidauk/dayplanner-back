from typing import Optional

from pydantic import BaseModel


class ActivityCreate(BaseModel):
    title: str
    description: str
    location: Optional[str] = ""
    duration: Optional[str] = "1 heure"


class ActivityResponse(ActivityCreate):
    id: int

    model_config = {
        "from_attributes": True
    }
