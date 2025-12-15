from cryptography.fernet import Fernet
import os
from datetime import datetime, timedelta
from jose import jwt

fernet = Fernet(os.environ["SECRET_KEY"].encode())


def encrypt_token(token: str) -> str:
    return fernet.encrypt(token.encode()).decode()


def decrypt_token(token_encrypted: str) -> str:
    return fernet.decrypt(token_encrypted.encode()).decode()


def create_jwt(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=60 * 24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, os.environ["JWT_SECRET"], algorithm="HS256")
