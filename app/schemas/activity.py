from pydantic import BaseModel


class ActivityCreate(BaseModel):
    title: str
    description: str
    location: str
    duration: str


class ActivityResponse(ActivityCreate):
    id: int

    model_config = {
        "from_attributes": True
    }