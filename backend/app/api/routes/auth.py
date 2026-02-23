from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.models import User
from app.schemas.common import Token
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.permissions import get_user_roles
from app.config import settings
from app.api.deps import get_current_active_user

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT tokens"""
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Get user roles
    user_roles = get_user_roles(db, user.id)

    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "roles": user_roles},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": user.id}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    payload = decode_token(request.refresh_token)

    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user"
        )

    # Get user roles
    user_roles = get_user_roles(db, user.id)

    # Create new tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "roles": user_roles},
        expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": user.id}
    )

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active
    }


class UpdateProfileRequest(BaseModel):
    """Payload for updating current user's basic profile information."""
    email: EmailStr | None = None
    full_name: str | None = None


class ChangePasswordRequest(BaseModel):
    """Payload for changing current user's password."""
    current_password: str
    new_password: str


@router.patch("/me")
async def update_current_user_profile(
    payload: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update current user's own profile (email, full_name)."""
    data = payload.dict(exclude_unset=True)

    # Prevent username changes here; only allow email/full_name
    if "email" in data:
        # Ensure email is unique
        existing = db.query(User).filter(
            User.email == data["email"],
            User.id != current_user.id,
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already in use",
            )
        current_user.email = data["email"]

    if "full_name" in data and data["full_name"] is not None:
        current_user.full_name = data["full_name"]

    db.commit()
    db.refresh(current_user)

    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
    }


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Allow an authenticated user to change their own password.

    - Verifies the current password
    - Applies bcrypt hashing to the new password
    """
    # Verify current password
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Basic guard to avoid setting same password; optional but helpful
    if verify_password(payload.new_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password",
        )

    current_user.password_hash = get_password_hash(payload.new_password)
    db.commit()

    return None
