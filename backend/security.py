"""
Authentication & authorization helpers:
- Password hashing (bcrypt via passlib)
- JWT creation & verification
- User registration & login helpers backed by MongoDB

NOTE: API surface intentionally mirrors the previous module so the app remains drop-in compatible.
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from pymongo import MongoClient

from .config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    MONGO_URI,
    MONGO_DB_NAME,
)

# OAuth2 token dependency (tokenUrl MUST stay "login" for compatibility)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Password hashing context
_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Mongo (very light abstraction)
_client = MongoClient(MONGO_URI)
_db = _client[MONGO_DB_NAME]
_users = _db["users"]


def _verify_password(plain: str, hashed: str) -> bool:
    return _pwd_ctx.verify(plain, hashed)


def _hash_password(plain: str) -> str:
    return _pwd_ctx.hash(plain)


def create_access_token(data: Dict[str, Any]) -> str:
    """
    Produce a signed JWT carrying the payload in `data` plus an expiry (`exp`).
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, str]:
    """
    Extract the current user from the Authorization: Bearer token.
    Raises 401 if invalid or the user no longer exists.
    """
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        if not user_id:
            raise cred_exc
    except JWTError:
        raise cred_exc

    user = _users.find_one({"_id": user_id})
    if not user:
        raise cred_exc

    return {"user_id": user["_id"], "email": user["email"]}


def register_user(email: str, password: str) -> Optional[Dict[str, str]]:
    """
    Create a new user document with a random ID and hashed password.
    Returns None if the email already exists or the insert fails.
    """
    try:
        if _users.find_one({"email": email}):
            return None
        user_id = __import__("os").urandom(16).hex()
        user_doc = {
            "_id": user_id,
            "email": email,
            "hashed_password": _hash_password(password),
        }
        _users.insert_one(user_doc)
        return {"user_id": user_id, "email": email}
    except Exception:
        return None


def authenticate_user(email: str, password: str) -> Optional[Dict[str, str]]:
    """
    Return minimal user info if the provided credentials are valid, else None.
    """
    user = _users.find_one({"email": email})
    if not user or not _verify_password(password, user.get("hashed_password", "")):
        return None
    return {"user_id": user["_id"], "email": user["email"]}
