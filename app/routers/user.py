from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.authentication.auth import hash_password
from app.authentication.security import get_current_user
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
    hashed_password = hash_password(user.password)
    db_user = User(name=user.name, surname=user.surname, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/current_user")
def get_current_user(user: User = Depends(get_current_user)):
    return {
        "name": user.name,
        "surname": user.surname,
        "email": user.email,
    }


@router.put("/user_info", response_model=UserInfoResponse)
def add_user_info(user_info: UserInfoCreate,
                  user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    db_user_info = db.query(UserInfo).filter_by(user_id=user.id).first()
    if db_user_info:
        db_user_info.place = user_info.place
        db_user_info.interests = user_info.interests
    else:
        db_user_info = UserInfo(user_id=user.id, place=user_info.place, interests=user_info.interests)
    db.add(db_user_info)
    db.commit()
    db.refresh(db_user_info)
    return db_user_info


@router.get("/user_info", response_model=UserInfoResponse)
def get_user_info(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user_info = db.query(UserInfo).filter_by(user_id=user.id).first()
    if not db_user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User info not found"
        )
    return db_user_info
