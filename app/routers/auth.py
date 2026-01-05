from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from starlette.requests import Request
from sqlalchemy.orm import Session
from app.authentication.auth import oauth
from app.database.database import get_db
from app.models.google_account import GoogleAccount
from app.authentication.security import encrypt_token, create_jwt, get_current_user, decrypt_token
from app.models.user import User
from config import REDIRECT_URI_LOGIN, FRONTEND_URL
import requests

router = APIRouter()


@router.get("/google/login")
async def login_via_google(request: Request):
    redirect_uri = REDIRECT_URI_LOGIN
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    userinfo = await oauth.google.userinfo(token=token)

    google_sub = userinfo["sub"]
    email = userinfo["email"]

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
    user = db.query(User).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.google_account_id = account.id
    db.add(user)
    db.commit()
    db.refresh(user)
    jwt = create_jwt({"sub": google_sub})
    params = urlencode({"token": jwt})

    redirect_url = f"{FRONTEND_URL}/google-callback?{params}"
    return RedirectResponse(url=redirect_url)


@router.post("/logout")
def logout(user: User = Depends(get_current_user), db=Depends(get_db)):
    if user.google_account:
        access_token = decrypt_token(user.google_account.access_token)

        # Révoquer le token Google
        requests.post(
            "https://oauth2.googleapis.com/revoke",
            params={"token": access_token},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        # Nettoyage base
        user.google_account.access_token = None
        user.google_account.refresh_token = None
        user.google_account.token_expiry = None

        db.add(user.google_account)
        db.commit()

    return {
        "success": True,
        "message": "Logged out and Google access revoked"
    }

