"""
Security Module — JWT + Password Hashing
-------------------------------------------
Production-grade authentication with:
- bcrypt password hashing (direct, no passlib)
- JWT token creation and verification
- Role-based access control helpers
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, Header, status

from app.core.config import settings


# ── Password Hashing (direct bcrypt) ────────────────────────────

def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


# ── JWT Token Management ────────────────────────────────────────

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a signed JWT access token.

    Args:
        data: Payload dict (must include 'sub' for username)
        expires_delta: Custom expiration, defaults to config value
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT token.

    Returns:
        Token payload dict

    Raises:
        HTTPException 401 if token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── FastAPI Dependencies ────────────────────────────────────────

def _extract_token(authorization: str = Header(default="")) -> str:
    """Extract Bearer token from Authorization header."""
    token = authorization.replace("Bearer ", "").strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


def require_store_user(authorization: str = Header(default="")) -> dict:
    """Dependency: Require a valid store user JWT."""
    token = _extract_token(authorization)
    payload = decode_access_token(token)
    if payload.get("role") != "user":
        raise HTTPException(status_code=403, detail="Store user access required")
    return payload


def require_admin(authorization: str = Header(default="")) -> dict:
    """Dependency: Require a valid admin JWT."""
    token = _extract_token(authorization)
    payload = decode_access_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload


def require_hacker(authorization: str = Header(default="")) -> dict:
    """Dependency: Require a valid hacker JWT."""
    token = _extract_token(authorization)
    payload = decode_access_token(token)
    if payload.get("role") != "hacker":
        raise HTTPException(status_code=403, detail="Hacker access required")
    return payload


def optional_store_user(authorization: str = Header(default="")) -> Optional[dict]:
    """Dependency: Optionally verify a store user JWT. Returns None if no token."""
    token = authorization.replace("Bearer ", "").strip()
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        return payload
    except HTTPException:
        return None
