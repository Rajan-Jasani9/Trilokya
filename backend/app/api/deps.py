from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.core.security import decode_token
from app.core.permissions import get_user_roles, can_access_project, can_access_cte

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    token_type: str = payload.get("type")
    
    if username is None or token_type != "access":
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    return current_user


def require_role(required_role: str):
    """Dependency to require a specific role"""
    async def role_checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        user_roles = get_user_roles(db, current_user.id)
        if required_role not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role} role"
            )
        return current_user
    return role_checker


def require_minimum_role_level(required_level: int):
    """Dependency to require minimum role hierarchy level"""
    async def level_checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        from app.core.permissions import get_user_highest_role_level
        user_level = get_user_highest_role_level(db, current_user.id)
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires minimum role level {required_level}"
            )
        return current_user
    return level_checker


def check_project_access(project_id: int):
    """Dependency to check project access"""
    async def access_checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        if not can_access_project(db, current_user.id, project_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this project"
            )
        return current_user
    return access_checker


def check_cte_access(cte_id: int):
    """Dependency to check CTE access"""
    async def access_checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        if not can_access_cte(db, current_user.id, cte_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this CTE"
            )
        return current_user
    return access_checker
