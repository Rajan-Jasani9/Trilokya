from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Project, ProjectOrgUnit, ProjectMember, ProjectTechnology, ProjectTRLOverride
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectMemberCreate, ProjectTRLOverrideCreate
from app.api.deps import get_current_active_user, require_minimum_role_level, check_project_access
from app.core.permissions import get_user_highest_role_level

router = APIRouter()


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List projects accessible to current user"""
    from app.core.permissions import can_access_project
    from app.models import ProjectMember, UserOrgUnit, ProjectOrgUnit
    
    # SuperAdmin sees all
    if get_user_highest_role_level(db, current_user.id) >= 5:
        projects = db.query(Project).offset(skip).limit(limit).all()
    else:
        # Get user's accessible projects
        # Projects where user is a member
        member_projects = db.query(ProjectMember.project_id).filter(
            ProjectMember.user_id == current_user.id
        ).subquery()
        
        # Projects in user's org units (for Managers/Assistant Managers)
        user_org_units = db.query(UserOrgUnit.org_unit_id).filter(
            UserOrgUnit.user_id == current_user.id
        ).subquery()
        org_projects = db.query(ProjectOrgUnit.project_id).filter(
            ProjectOrgUnit.org_unit_id.in_(user_org_units)
        ).subquery()
        
        project_ids = set()
        for row in db.query(member_projects).all():
            project_ids.add(row[0])
        for row in db.query(org_projects).all():
            project_ids.add(row[0])
        
        projects = db.query(Project).filter(Project.id.in_(project_ids)).offset(skip).limit(limit).all()
    
    # Include current TRL and computed target TRL for each project
    from app.core.trl_engine import compute_project_trl, compute_project_target_trl
    from app.core.readiness_engine import compute_project_irl, compute_project_mrl, compute_project_srl
    for project in projects:
        project.current_trl = compute_project_trl(db, project.id)
        project.current_irl = compute_project_irl(db, project.id)
        project.current_mrl = compute_project_mrl(db, project.id)
        project.current_srl = compute_project_srl(db, project.id, project.current_trl)
        # Compute target TRL as min of all CTE target TRLs
        computed_target_trl = compute_project_target_trl(db, project.id)
        if computed_target_trl is not None:
            project.target_trl = computed_target_trl
        # Include technology IDs
        project.technology_ids = [pt.technology_id for pt in project.technologies]
    
    return projects


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_minimum_role_level(4))  # Manager or above
):
    """Create a new project (Manager/SuperAdmin only)"""
    # Check if project code already exists
    existing = db.query(Project).filter(Project.code == project_data.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project code already exists"
        )
    
    project = Project(
        code=project_data.code,
        name=project_data.name,
        description=project_data.description,
        category=project_data.category,
        target_trl=project_data.target_trl,
        start_date=project_data.start_date,
        end_date=project_data.end_date,
        created_by=current_user.id
    )
    db.add(project)
    db.flush()
    
    # Add org units
    for org_unit_id in project_data.org_unit_ids:
        project_org = ProjectOrgUnit(project_id=project.id, org_unit_id=org_unit_id)
        db.add(project_org)

    # Add technologies
    for tech_id in project_data.technology_ids:
        project_tech = ProjectTechnology(project_id=project.id, technology_id=tech_id)
        db.add(project_tech)
    
    db.commit()
    db.refresh(project)

    # Populate response fields
    project.technology_ids = [pt.technology_id for pt in project.technologies]
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get project details"""
    from app.api.deps import check_project_access
    await check_project_access(project_id)(current_user=current_user, db=db)
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get org unit IDs
    org_units = db.query(ProjectOrgUnit).filter(ProjectOrgUnit.project_id == project_id).all()
    project.org_unit_ids = [ou.org_unit_id for ou in org_units]

    # Get technology IDs
    techs = db.query(ProjectTechnology).filter(ProjectTechnology.project_id == project_id).all()
    project.technology_ids = [t.technology_id for t in techs]
    
    # Include members in response
    members = db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()
    project.members = [
        {
            "id": m.id,
            "user_id": m.user_id,
            "user": {
                "id": m.user.id,
                "username": m.user.username,
                "email": m.user.email,
                "full_name": m.user.full_name
            },
            "role_in_project": m.role_in_project
        }
        for m in members
    ]
    
    # Include current TRL
    from app.core.trl_engine import compute_project_trl, compute_project_target_trl
    from app.core.readiness_engine import compute_project_irl, compute_project_mrl, compute_project_srl
    project.current_trl = compute_project_trl(db, project_id)
    project.current_irl = compute_project_irl(db, project_id)
    project.current_mrl = compute_project_mrl(db, project_id)
    project.current_srl = compute_project_srl(db, project_id, project.current_trl)
    
    # Compute and set target TRL as min of all CTE target TRLs
    computed_target_trl = compute_project_target_trl(db, project_id)
    if computed_target_trl is not None:
        project.target_trl = computed_target_trl
    
    # Include TRL overrides
    overrides = db.query(ProjectTRLOverride).filter(
        ProjectTRLOverride.project_id == project_id
    ).order_by(ProjectTRLOverride.created_at.desc()).all()
    project.trl_overrides = [
        {
            "id": o.id,
            "trl_value": o.trl_value,
            "reason": o.reason,
            "created_at": o.created_at
        }
        for o in overrides
    ]
    
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_minimum_role_level(4)),  # Manager or SuperAdmin
):
    """Delete a project and all related CTEs, members, and assessments (cascade)."""
    from app.api.deps import check_project_access

    await check_project_access(project_id)(current_user=current_user, db=db)

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    db.delete(project)
    db.commit()
    return None


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Update project"""
    from app.api.deps import check_project_access
    await check_project_access(project_id)(current_user=current_user, db=db)
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    update_data = project_data.dict(exclude_unset=True)
    org_unit_ids = update_data.pop("org_unit_ids", None)
    technology_ids = update_data.pop("technology_ids", None)
    
    for field, value in update_data.items():
        setattr(project, field, value)
    
    if org_unit_ids is not None:
        # Update org units
        db.query(ProjectOrgUnit).filter(ProjectOrgUnit.project_id == project_id).delete()
        for org_unit_id in org_unit_ids:
            project_org = ProjectOrgUnit(project_id=project_id, org_unit_id=org_unit_id)
            db.add(project_org)

    if technology_ids is not None:
        # Update technologies
        db.query(ProjectTechnology).filter(ProjectTechnology.project_id == project_id).delete()
        for tech_id in technology_ids:
            project_tech = ProjectTechnology(project_id=project_id, technology_id=tech_id)
            db.add(project_tech)
    
    db.commit()
    db.refresh(project)
    
    # Compute and set target TRL as min of all CTE target TRLs
    from app.core.trl_engine import compute_project_target_trl
    computed_target_trl = compute_project_target_trl(db, project_id)
    if computed_target_trl is not None:
        project.target_trl = computed_target_trl
        db.commit()
        db.refresh(project)
    
    # Get org unit IDs for response
    org_units = db.query(ProjectOrgUnit).filter(ProjectOrgUnit.project_id == project_id).all()
    project.org_unit_ids = [ou.org_unit_id for ou in org_units]

    # Get technology IDs for response
    techs = db.query(ProjectTechnology).filter(ProjectTechnology.project_id == project_id).all()
    project.technology_ids = [t.technology_id for t in techs]
    
    return project


@router.get("/{project_id}/members")
async def get_project_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get project members"""
    from app.api.deps import check_project_access
    await check_project_access(project_id)(current_user=current_user, db=db)
    
    members = db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()
    return [
        {
            "id": m.id,
            "user_id": m.user_id,
            "user": {
                "id": m.user.id,
                "username": m.user.username,
                "email": m.user.email,
                "full_name": m.user.full_name
            },
            "role_in_project": m.role_in_project,
            "assigned_at": m.assigned_at
        }
        for m in members
    ]


@router.post("/{project_id}/members", status_code=status.HTTP_201_CREATED)
async def add_project_member(
    project_id: int,
    member_data: ProjectMemberCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_minimum_role_level(3))  # Assistant Manager or above
):
    """Add member to project"""
    from app.api.deps import check_project_access
    await check_project_access(project_id)(current_user=current_user, db=db)
    
    # Check if already a member
    existing = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == member_data.user_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this project"
        )
    
    member = ProjectMember(
        project_id=project_id,
        user_id=member_data.user_id,
        role_in_project=member_data.role_in_project
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return {
        "id": member.id,
        "user_id": member.user_id,
        "message": "Member added successfully"
    }


@router.delete("/{project_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_project_member(
    project_id: int,
    member_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_minimum_role_level(3))  # Assistant Manager or above
):
    """Remove member from project"""
    from app.api.deps import check_project_access
    await check_project_access(project_id)(current_user=current_user, db=db)
    
    member = db.query(ProjectMember).filter(
        ProjectMember.id == member_id,
        ProjectMember.project_id == project_id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    db.delete(member)
    db.commit()
    return None


@router.post("/{project_id}/trl-override", status_code=status.HTTP_201_CREATED)
async def override_project_trl(
    project_id: int,
    override_data: ProjectTRLOverrideCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_minimum_role_level(4))  # Manager or above
):
    """Override project TRL (Manager/SuperAdmin only)"""
    from app.api.deps import check_project_access
    await check_project_access(project_id)(current_user=current_user, db=db)
    
    override = ProjectTRLOverride(
        project_id=project_id,
        trl_value=override_data.trl_value,
        overridden_by=current_user.id,
        reason=override_data.reason
    )
    db.add(override)
    db.commit()
    return {"message": "TRL override created successfully"}
