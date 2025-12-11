from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    surname: str
    email: str


class UserResponse(UserCreate):
    id: int

    class Config:
        orm_mode = True
