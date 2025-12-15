from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request
from sqlalchemy.orm import Session
from app.authentication.auth import oauth
from app.database.database import get_db
from app.models.google_account import GoogleAccount
from app.authentication.security import encrypt_token, create_jwt
from app.models.user import User

router = APIRouter()


@router.get("/google/login")
async def login_via_google(request: Request):
    redirect_uri = "http://localhost:8000/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    print(f"request = {request}")
    token = await oauth.google.authorize_access_token(request)
    id_token = await oauth.google.parse_id_token(request, token)

    google_sub = id_token["sub"]
    email = id_token["email"]

    account = db.query(GoogleAccount).filter_by(google_sub=google_sub).first()
    if not account:
        account = GoogleAccount(google_sub=google_sub, email=email)
        db.add(account)
    account.access_token = encrypt_token(token["access_token"])
    if "refresh_token" in token:
        account.refresh_token = encrypt_token(token["refresh_token"])
    account.token_expiry = datetime.utcnow() + timedelta(seconds=token["expires_in"])
    db.commit()
    db.refresh(account)
    user = db.query(User).filter_by(email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.google_account_id = account.id
    db.add(user)
    db.commit()
    db.refresh(user)
    jwt = create_jwt({"sub": google_sub})
    return {
        "access_token": jwt,
        "token_type": "bearer",
        "authenticated": True
    }
