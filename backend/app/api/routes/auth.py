"""
Authentication Routes
-----------------------
Registration and login endpoints for all user roles:
- Store users (customers)
- Hacker users (attack console)
All responses follow the standard JSON format.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.db_models import User, HackerUser
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ═══════════════════════════════════════════════════════════════════
#  REQUEST / RESPONSE SCHEMAS
# ═══════════════════════════════════════════════════════════════════

class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: str = Field(min_length=5, max_length=128)
    password: str = Field(min_length=6, max_length=128)
    full_name: str = Field(default="", max_length=128)


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    success: bool
    message: str = ""
    token: str | None = None
    user: dict | None = None


class HackerRegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)
    alias: str = Field(default="phantom", max_length=64)


# ═══════════════════════════════════════════════════════════════════
#  STORE USER AUTH
# ═══════════════════════════════════════════════════════════════════

@router.post("/register", response_model=AuthResponse)
async def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new store customer."""
    # Check existing
    existing = db.query(User).filter(
        (User.username == request.username) | (User.email == request.email)
    ).first()
    if existing:
        return AuthResponse(success=False, message="Username or email already exists")

    user = User(
        username=request.username,
        email=request.email,
        hashed_password=hash_password(request.password),
        full_name=request.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({
        "sub": user.username,
        "user_id": user.id,
        "role": "user",
    })

    logger.info("New store user registered: %s", user.username)

    return AuthResponse(
        success=True,
        message="Registration successful",
        token=token,
        user={"id": user.id, "username": user.username, "email": user.email, "full_name": user.full_name},
    )


@router.post("/login", response_model=AuthResponse)
async def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    """Login a store customer."""
    user = db.query(User).filter(User.username == request.username).first()

    if not user or not verify_password(request.password, user.hashed_password):
        return AuthResponse(success=False, message="Invalid username or password")

    if not user.is_active:
        return AuthResponse(success=False, message="Account is deactivated")

    token = create_access_token({
        "sub": user.username,
        "user_id": user.id,
        "role": "user",
    })

    logger.info("Store user login: %s", user.username)

    return AuthResponse(
        success=True,
        message="Login successful",
        token=token,
        user={"id": user.id, "username": user.username, "email": user.email, "full_name": user.full_name},
    )


# ═══════════════════════════════════════════════════════════════════
#  HACKER USER AUTH
# ═══════════════════════════════════════════════════════════════════

@router.post("/hacker/register", response_model=AuthResponse)
async def register_hacker(request: HackerRegisterRequest, db: Session = Depends(get_db)):
    """Register a new hacker console user."""
    existing = db.query(HackerUser).filter(HackerUser.username == request.username).first()
    if existing:
        return AuthResponse(success=False, message="Username already taken")

    hacker = HackerUser(
        username=request.username,
        hashed_password=hash_password(request.password),
        alias=request.alias,
    )
    db.add(hacker)
    db.commit()
    db.refresh(hacker)

    token = create_access_token({
        "sub": hacker.username,
        "user_id": hacker.id,
        "role": "hacker",
    })

    logger.info("New hacker user registered: %s (alias: %s)", hacker.username, hacker.alias)

    return AuthResponse(
        success=True,
        message="Hacker registration successful",
        token=token,
        user={"id": hacker.id, "username": hacker.username, "alias": hacker.alias},
    )


@router.post("/hacker/login", response_model=AuthResponse)
async def login_hacker(request: LoginRequest, db: Session = Depends(get_db)):
    """Login a hacker console user."""
    hacker = db.query(HackerUser).filter(HackerUser.username == request.username).first()

    if not hacker or not verify_password(request.password, hacker.hashed_password):
        return AuthResponse(success=False, message="Invalid username or password")

    if not hacker.is_active:
        return AuthResponse(success=False, message="Account is deactivated")

    token = create_access_token({
        "sub": hacker.username,
        "user_id": hacker.id,
        "role": "hacker",
    })

    logger.info("Hacker login: %s", hacker.username)

    return AuthResponse(
        success=True,
        message="Login successful",
        token=token,
        user={"id": hacker.id, "username": hacker.username, "alias": hacker.alias},
    )
