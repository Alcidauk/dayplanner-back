from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.database.database import get_db
router = APIRouter()


@router.put("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        User.name == user.name,
        User.surname == user.surname,
        User.email == user.email
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Author already registered")
    db_user = User(name=user.name, surname=user.surname, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
