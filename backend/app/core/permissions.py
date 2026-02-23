from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import User, Role, UserRole, Project, CTE, ProjectMember


# Role hierarchy levels
ROLE_HIERARCHY = {
    "SuperAdmin": 5,
    "Manager": 4,
    "Assistant Manager": 3,
    "Engineer": 2,
    "Scientist": 2,
}


def get_user_roles(db: Session, user_id: int, org_unit_id: Optional[int] = None) -> List[str]:
    """Get user's roles, optionally filtered by org unit"""
    query = db.query(UserRole).join(Role).filter(UserRole.user_id == user_id)
    if org_unit_id:
        query = query.filter(UserRole.org_unit_id == org_unit_id)
    user_roles = query.all()
    return [ur.role.name for ur in user_roles]


def get_user_highest_role_level(db: Session, user_id: int, org_unit_id: Optional[int] = None) -> int:
    """Get user's highest role hierarchy level"""
    roles = get_user_roles(db, user_id, org_unit_id)
    if not roles:
        return 0
    return max([ROLE_HIERARCHY.get(role, 0) for role in roles])


def has_role(user_roles: List[str], required_role: str) -> bool:
    """Check if user has a specific role"""
    return required_role in user_roles


def has_minimum_role_level(user_hierarchy_level: int, required_level: int) -> bool:
    """Check if user has minimum role hierarchy level"""
    return user_hierarchy_level >= required_level


def can_access_project(db: Session, user_id: int, project_id: int) -> bool:
    """Check if user can access a project"""
    # SuperAdmin can access everything
    if has_role(get_user_roles(db, user_id), "SuperAdmin"):
        return True
    
    # Check if user is assigned to project
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()
    if member:
        return True
    
    # Check if user is Manager/Assistant Manager of project's org unit
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return False
    
    # Get user's org units
    from app.models import UserOrgUnit
    user_org_units = db.query(UserOrgUnit).filter(UserOrgUnit.user_id == user_id).all()
    user_org_unit_ids = [uo.org_unit_id for uo in user_org_units]
    
    # Check if project belongs to user's org units
    from app.models import ProjectOrgUnit
    project_org_units = db.query(ProjectOrgUnit).filter(ProjectOrgUnit.project_id == project_id).all()
    project_org_unit_ids = [po.org_unit_id for po in project_org_units]
    
    if not set(user_org_unit_ids).intersection(set(project_org_unit_ids)):
        return False
    
    # Check if user has Manager or Assistant Manager role in those org units
    user_roles = get_user_roles(db, user_id)
    if "Manager" in user_roles or "Assistant Manager" in user_roles:
        return True
    
    return False


def can_access_cte(db: Session, user_id: int, cte_id: int) -> bool:
    """Check if user can access a CTE"""
    cte = db.query(CTE).filter(CTE.id == cte_id).first()
    if not cte:
        return False
    
    # If user can access project, they can access CTE
    return can_access_project(db, user_id, cte.project_id)


def require_role(required_role: str):
    """Decorator to require a specific role"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This will be used in route dependencies
            pass
        return wrapper
    return decorator


def require_permission(action: str, resource: str):
    """Decorator to require a specific permission"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This will be used in route dependencies
            pass
        return wrapper
    return decorator
