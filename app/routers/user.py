from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.authentication.auth import hash_password
from app.authentication.security import get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.database.database import get_db

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        User.name == user.name,
        User.surname == user.surname,
        User.email == user.email
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already registered")
    hashed_password = hash_password(user.password)
    db_user = User(name=user.name, surname=user.surname, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/current_user")
def get_logged_user(user: User = Depends(get_current_user)):
    return {
        "name": user.name,
        "surname": user.surname,
        "email": user.email,
        "google_account_id": user.google_account_id
    }
