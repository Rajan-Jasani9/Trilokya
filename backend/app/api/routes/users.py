from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db
from app.models import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.api.deps import get_current_active_user, require_role
from app.core.security import get_password_hash

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("SuperAdmin"))
):
    """List all users (SuperAdmin only)"""
    from app.models.user import UserOrgUnit, UserRole
    from app.schemas.user import OrgUnitResponse, RoleResponse
    
    users = db.query(User).options(
        joinedload(User.org_units).joinedload(UserOrgUnit.org_unit),
        joinedload(User.roles).joinedload(UserRole.role)
    ).offset(skip).limit(limit).all()
    
    # Transform users to include proper org_units and roles
    result = []
    for user in users:
        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "org_units": [
                OrgUnitResponse(
                    id=uo.org_unit.id,
                    code=uo.org_unit.code,
                    name=uo.org_unit.name,
                    parent_id=uo.org_unit.parent_id,
                    org_type=uo.org_unit.org_type,
                    created_at=uo.org_unit.created_at
                ) for uo in user.org_units
            ],
            "roles": [
                RoleResponse(
                    id=ur.role.id,
                    name=ur.role.name,
                    hierarchy_level=ur.role.hierarchy_level,
                    permissions_json=ur.role.permissions_json or {}
                ) for ur in user.roles
            ]
        }
        result.append(user_dict)
    
    return result


@router.get("/accessible", response_model=List[UserResponse])
async def list_accessible_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List users accessible to current user for project assignment"""
    from app.models.user import UserOrgUnit, UserRole
    from app.schemas.user import OrgUnitResponse, RoleResponse
    from app.core.permissions import get_user_highest_role_level
    
    # SuperAdmin sees all
    if get_user_highest_role_level(db, current_user.id) >= 5:
        users = db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    else:
        # Managers/Assistant Managers see users in their org units
        user_org_unit_ids = [
            uo.org_unit_id for uo in db.query(UserOrgUnit).filter(
                UserOrgUnit.user_id == current_user.id
            ).all()
        ]
        
        if user_org_unit_ids:
            # Get users in same org units
            user_ids_in_org = [
                uo.user_id for uo in db.query(UserOrgUnit).filter(
                    UserOrgUnit.org_unit_id.in_(user_org_unit_ids)
                ).distinct().all()
            ]
            
            users = db.query(User).filter(
                User.id.in_(user_ids_in_org),
                User.is_active == True
            ).offset(skip).limit(limit).all()
        else:
            # No org units, return empty
            users = []
    
    # Transform users to include proper org_units and roles
    users_with_relations = db.query(User).options(
        joinedload(User.org_units).joinedload(UserOrgUnit.org_unit),
        joinedload(User.roles).joinedload(UserRole.role)
    ).filter(User.id.in_([u.id for u in users])).all() if users else []
    
    result = []
    for user in users_with_relations:
        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "org_units": [
                OrgUnitResponse(
                    id=uo.org_unit.id,
                    code=uo.org_unit.code,
                    name=uo.org_unit.name,
                    parent_id=uo.org_unit.parent_id,
                    org_type=uo.org_unit.org_type,
                    created_at=uo.org_unit.created_at
                ) for uo in user.org_units
            ],
            "roles": [
                RoleResponse(
                    id=ur.role.id,
                    name=ur.role.name,
                    hierarchy_level=ur.role.hierarchy_level,
                    permissions_json=ur.role.permissions_json or {}
                ) for ur in user.roles
            ]
        }
        result.append(user_dict)
    
    return result


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("SuperAdmin"))
):
    """Create a new user (SuperAdmin only)"""
    # Check if username or email already exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )
    
    hashed_password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("SuperAdmin"))
):
    """Update user (SuperAdmin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    update_data = user_data.dict(exclude_unset=True)
    
    # Handle password update separately if provided
    if 'password' in update_data:
        from app.core.security import get_password_hash
        user.password_hash = get_password_hash(update_data.pop('password'))
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("SuperAdmin"))
):
    """Delete user (SuperAdmin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    db.delete(user)
    db.commit()
    return None
