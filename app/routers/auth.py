from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from starlette.requests import Request
from sqlalchemy.orm import Session
from app.authentication.auth import oauth, verify_password
from app.database.database import get_db
from app.models.google_account import GoogleAccount
from app.models.token import Token
from app.authentication.security import encrypt_token, create_jwt, get_current_user, decrypt_token
from app.models.user import User
from app.schemas.user import LoginResponse, LoginRequest
from config import REDIRECT_URI_LOGIN, FRONTEND_URL
import requests
import secrets

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="email not found"
        )

    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )

    access_token = create_jwt({"sub": str(user.id)})
    refresh_token_str = secrets.token_urlsafe(32)
    expiry = datetime.utcnow() + timedelta(days=30)

    token_obj = Token(
        access_token=encrypt_token(access_token),
        refresh_token=encrypt_token(refresh_token_str),
        token_expiry=expiry,
        user_id=user.id
    )
    db.add(token_obj)
    db.commit()
    db.refresh(token_obj)

    user.token_id = token_obj.id
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_expiry": expiry.isoformat(),
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
        }
    }


@router.get("/google/login")
async def login_via_google(request: Request):
    redirect_uri = REDIRECT_URI_LOGIN
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    token_data = await oauth.google.authorize_access_token(request)
    userinfo = await oauth.google.userinfo(token=token_data)

    google_sub = userinfo["sub"]
    email = userinfo["email"]

    account = db.query(GoogleAccount).filter_by(google_sub=google_sub).first()
    if not account:
        account = GoogleAccount(google_sub=google_sub, email=email)
        db.add(account)
        db.commit()
        db.refresh(account)

    user = db.query(User).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = Token(
        access_token=encrypt_token(token_data.get("access_token")),
        refresh_token=encrypt_token(token_data.get("refresh_token")),
        token_expiry=datetime.utcnow() + timedelta(seconds=token_data.get("expires_in")),
        google_account_id=account.id,
        user_id=user.id
    )
    db.add(token)
    db.commit()
    db.refresh(token)

    user.token_id = token.id
    user.google_account_id = account.id
    db.add(user)
    db.commit()
    db.refresh(user)

    account.token_id = token.id
    account.user_id = user.id
    db.add(account)
    db.commit()

    jwt = create_jwt({"sub": str(user.id)})
    params = urlencode({"token": jwt})

    redirect_url = f"{FRONTEND_URL}/google-callback?{params}"
    return RedirectResponse(url=redirect_url)


@router.post("/logout")
def logout(user: User = Depends(get_current_user), db=Depends(get_db)):
    if user.token:
        if user.google_account:
            try:
                access_token = decrypt_token(user.token.access_token)
                requests.post(
                    "https://oauth2.googleapis.com/revoke",
                    params={"token": access_token},
                    headers={"content-type": "application/x-www-form-urlencoded"},
                    timeout=5
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Erreur lors de la révocation Google: {e}")

        user.token_id = None
        db.add(user)
        db.commit()
        user_tokens = db.query(Token).filter(Token.user_id == user.id).all()
        for token in user_tokens:
            db.delete(token)
        db.commit()

    redirect_url = f"{FRONTEND_URL}/"
    return RedirectResponse(url=redirect_url)
