from datetime import datetime

from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    surname: str
    email: str


class UserResponse(UserCreate):
    id: int

    class Config:
        orm_mode = True



class UserInfoCreate(BaseModel):
    place: str
    interest: dict


class UserInfoResponse(UserInfoCreate):
    id: int

    class Config:
        orm_mode = True


class UserAvailabilityCreate(BaseModel):
    starting_hour: str
    ending_hour: datetime
    available_days: dict


class UserAvailabilityResponse(UserAvailabilityCreate):
    id: int

    class Config:
        orm_mode = True
