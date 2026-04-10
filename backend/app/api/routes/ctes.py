from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import CTE, Project
from app.schemas.cte import CTECreate, CTEUpdate, CTEResponse
from app.api.deps import get_current_active_user, check_project_access, require_minimum_role_level

router = APIRouter()


@router.get("/projects/{project_id}/ctes", response_model=List[CTEResponse])
async def list_ctes(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List CTEs for a project"""
    await check_project_access(project_id)(current_user=current_user, db=db)
    
    ctes = db.query(CTE).filter(CTE.project_id == project_id).all()
    return ctes


@router.post("/projects/{project_id}/ctes", response_model=CTEResponse, status_code=status.HTTP_201_CREATED)
async def create_cte(
    project_id: int,
    cte_data: CTECreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create a new CTE"""
    await check_project_access(project_id)(current_user=current_user, db=db)
    
    cte = CTE(
        project_id=project_id,
        code=cte_data.code,
        name=cte_data.name,
        description=cte_data.description,
        category=cte_data.category,
        target_trl=cte_data.target_trl
    )
    db.add(cte)
    db.commit()
    db.refresh(cte)
    
    # Update project target TRL as min of all CTE target TRLs
    from app.core.trl_engine import compute_project_target_trl
    computed_target_trl = compute_project_target_trl(db, project_id)
    if computed_target_trl is not None:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.target_trl = computed_target_trl
            db.commit()
    
    return cte


@router.delete("/{cte_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cte(
    cte_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_minimum_role_level(4)),  # Manager or SuperAdmin
):
    """Delete a CTE and its assessments (cascade). Recomputes project target TRL."""
    from app.api.deps import check_cte_access
    from app.core.trl_engine import compute_project_target_trl

    await check_cte_access(cte_id)(current_user=current_user, db=db)

    cte = db.query(CTE).filter(CTE.id == cte_id).first()
    if not cte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CTE not found",
        )

    project_id = cte.project_id
    db.delete(cte)
    db.commit()

    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        computed = compute_project_target_trl(db, project_id)
        project.target_trl = computed
        db.commit()

    return None


@router.get("/{cte_id}", response_model=CTEResponse)
async def get_cte(
    cte_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get CTE details"""
    from app.api.deps import check_cte_access
    await check_cte_access(cte_id)(current_user=current_user, db=db)
    
    cte = db.query(CTE).filter(CTE.id == cte_id).first()
    if not cte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CTE not found"
        )
    return cte


@router.patch("/{cte_id}", response_model=CTEResponse)
async def update_cte(
    cte_id: int,
    cte_data: CTEUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Update CTE"""
    from app.api.deps import check_cte_access
    await check_cte_access(cte_id)(current_user=current_user, db=db)
    
    cte = db.query(CTE).filter(CTE.id == cte_id).first()
    if not cte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CTE not found"
        )
    
    update_data = cte_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cte, field, value)
    
    db.commit()
    db.refresh(cte)
    
    # Update project target TRL as min of all CTE target TRLs
    from app.core.trl_engine import compute_project_target_trl
    computed_target_trl = compute_project_target_trl(db, cte.project_id)
    if computed_target_trl is not None:
        project = db.query(Project).filter(Project.id == cte.project_id).first()
        if project:
            project.target_trl = computed_target_trl
            db.commit()
    
    return cte
