from datetime import datetime, timedelta
import hashlib
import os
from fastapi import HTTPException, Request
from passlib.context import CryptContext
from jose import JWTError, jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_pass: str) -> str:
    # Pre-hash with SHA-256 to handle passwords longer than 72 bytes
    # SHA-256 produces a fixed-length 64-character hex string
    prehashed = hashlib.sha256(plain_pass.encode("utf-8")).hexdigest()
    return pwd_context.hash(prehashed)


def verify_password(plain_pass: str, hashed_pass: str) -> bool:
    # Pre-hash the plain password the same way before verification
    prehashed = hashlib.sha256(plain_pass.encode("utf-8")).hexdigest()
    return pwd_context.verify(prehashed, hashed_pass)


SECRET_KEY = os.getenv("TOKEN_SECRET", "admin1234@")
ACCESS_TOKEN_EXPIRE_MINUTES = 60
ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def auth_guard(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authorised")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    request.state.user = payload.get("auth_user")
    return payload.get("auth_user")
