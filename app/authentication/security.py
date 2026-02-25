from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from jose import jwt

from app.database.database import get_db
from app.models.user import User
from config import SECRET_KEY, JWT_SECRET
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from constants import FIFTEEN_MINUTES_ACCESS_TOKEN_DURATION

import hmac
import hashlib


def hash_token(token: str) -> str:
    return hmac.new(SECRET_KEY.encode("utf-8"), token.encode(), hashlib.sha256).hexdigest()


fernet = Fernet(SECRET_KEY.encode())


def encrypt_token(token: str) -> str:
    return fernet.encrypt(token.encode()).decode()


def decrypt_token(token_encrypted: str) -> str:
    return fernet.decrypt(token_encrypted.encode()).decode()


def create_jwt(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=FIFTEEN_MINUTES_ACCESS_TOKEN_DURATION)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token_str = credentials.credentials
    try:
        payload = jwt.decode(token_str, JWT_SECRET, algorithms=["HS256"])
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        user_id = int(sub)

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
