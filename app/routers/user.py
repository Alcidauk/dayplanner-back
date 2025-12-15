from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.user_info import UserInfo
from app.schemas.user import UserCreate, UserResponse
from app.schemas.user_info import UserInfoCreate, UserInfoResponse
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
        raise HTTPException(status_code=400, detail="User already registered")
    db_user = User(name=user.name, surname=user.surname, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.put("/user_info", response_model=UserInfoResponse)
def add_user_info(user_info: UserInfoCreate, db: Session = Depends(get_db)):
    # TODO voir comment on fait pour un user_info existant, sûrement en vérifiant si la clé étrangère du user est déjà
    #  existante
    db_user_info = UserInfo(place=user_info.place, interests=user_info.interest)
    db.add(db_user_info)
    db.commit()
    db.refresh(db_user_info)
    return db_user_info
