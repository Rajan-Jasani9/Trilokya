from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from typing import List
from app.database import get_db
from app.models.technology import Technology
from app.models.project import ProjectTechnology
from app.schemas.technology import TechnologyCreate, TechnologyUpdate, TechnologyResponse
from app.api.deps import get_current_active_user, require_minimum_role_level

router = APIRouter()

MEDIA_BASE_URL = "/media/technologies"


def _enrich(tech, db):
    """Attach computed fields: project_count, icon_url."""
    tech.project_count = (
        db.query(sql_func.count(ProjectTechnology.project_id))
        .filter(ProjectTechnology.technology_id == tech.id)
        .scalar()
        or 0
    )
    tech.icon_url = (
        f"{MEDIA_BASE_URL}/{tech.icon_filename}" if tech.icon_filename else None
    )
    return tech


@router.get("/", response_model=List[TechnologyResponse])
async def list_technologies(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """List all technologies, optionally filtered to active only"""
    query = db.query(Technology)
    if active_only:
        query = query.filter(Technology.is_active == True)
    technologies = query.order_by(Technology.display_order, Technology.name).all()

    for tech in technologies:
        _enrich(tech, db)

    return technologies


@router.get("/{technology_id}", response_model=TechnologyResponse)
async def get_technology(
    technology_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Get a single technology"""
    tech = db.query(Technology).filter(Technology.id == technology_id).first()
    if not tech:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Technology not found")

    return _enrich(tech, db)


@router.get("/{technology_id}/projects")
async def list_projects_by_technology(
    technology_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """List all projects under a technology"""
    from app.models import Project
    from app.core.trl_engine import compute_project_trl, compute_project_target_trl

    tech = db.query(Technology).filter(Technology.id == technology_id).first()
    if not tech:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Technology not found")

    project_ids = (
        db.query(ProjectTechnology.project_id)
        .filter(ProjectTechnology.technology_id == technology_id)
        .all()
    )
    project_id_list = [pid[0] for pid in project_ids]

    projects = db.query(Project).filter(Project.id.in_(project_id_list)).all()

    for project in projects:
        project.current_trl = compute_project_trl(db, project.id)
        computed_target_trl = compute_project_target_trl(db, project.id)
        if computed_target_trl is not None:
            project.target_trl = computed_target_trl

    return projects


@router.post("/", response_model=TechnologyResponse, status_code=status.HTTP_201_CREATED)
async def create_technology(
    tech_data: TechnologyCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_minimum_role_level(5)),
):
    """Create a new technology (SuperAdmin only)"""
    existing = db.query(Technology).filter(Technology.name == tech_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Technology with this name already exists",
        )

    tech = Technology(
        name=tech_data.name,
        description=tech_data.description,
        icon_filename=tech_data.icon_filename,
        is_active=tech_data.is_active,
        display_order=tech_data.display_order,
    )
    db.add(tech)
    db.commit()
    db.refresh(tech)
    tech.project_count = 0
    tech.icon_url = (
        f"{MEDIA_BASE_URL}/{tech.icon_filename}" if tech.icon_filename else None
    )
    return tech


@router.patch("/{technology_id}", response_model=TechnologyResponse)
async def update_technology(
    technology_id: int,
    tech_data: TechnologyUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_minimum_role_level(5)),
):
    """Update a technology (SuperAdmin only)"""
    tech = db.query(Technology).filter(Technology.id == technology_id).first()
    if not tech:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Technology not found")

    update_data = tech_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tech, field, value)

    db.commit()
    db.refresh(tech)
    return _enrich(tech, db)
