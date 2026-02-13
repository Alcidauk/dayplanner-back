from fastapi import APIRouter, status, Depends, HTTPException
from app.database.database import get_db
from app.models.user_info import UserInfo
from app.schemas.user_info import UserInfoResponse, UserInfoCreate
from app.authentication.security import get_current_user
from sqlalchemy.orm import Session
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=UserInfoResponse)
def get_user_info(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user_info = db.query(UserInfo).filter_by(user_id=user.id).first()
    if not db_user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User info not found"
        )
    return db_user_info


@router.post("/", response_model=UserInfoResponse)
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


@router.post("/add_interest", response_model=UserInfoResponse)
def add_single_interest(request_body: dict,
                        user: User = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    db_user_info = db.query(UserInfo).filter_by(user_id=user.id).first()
    if not db_user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User info not found. Please create user info first."
        )
    existing_interests = db_user_info.interests or []
    if request_body['interest'] in existing_interests:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interest already exists"
        )
    db_user_info.interests = existing_interests + [request_body['interest']]
    db.commit()
    db.refresh(db_user_info)
    return db_user_info


@router.delete("/remove_interest", response_model=UserInfoResponse)
def remove_single_interest(data: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user_info = db.query(UserInfo).filter_by(user_id=user.id).first()
    if not db_user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User info not found"
        )
    existing_interests = db_user_info.interests or []
    if data['interest'] not in existing_interests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interest not found"
        )
    db_user_info.interests = [i for i in existing_interests if i != data['interest']]
    db.commit()
    db.refresh(db_user_info)
    return db_user_info


@router.put("/update_place", response_model=UserInfoResponse)
def update_place(data: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user_info = db.query(UserInfo).filter_by(user_id=user.id).first()
    if not db_user_info:
        db_user_info = UserInfo(user_id=user.id, place=data['place'], interests=[])
        db.add(db_user_info)
    else:
        db_user_info.place = data['place']
    db.commit()
    db.refresh(db_user_info)
    return db_user_info
