"""Projects API endpoints"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Project
from app.schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from app.core.logger import get_logger
from app.core.auth import require_admin
from app.core.config import settings

logger = get_logger(__name__)
router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse, dependencies=[Depends(require_admin)])
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    """Create a new project (admin only)"""
    existing = db.query(Project).filter(Project.repo_full_name == project.repo_full_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Project with this repo already exists")

    db_data = project.dict()
    if not db_data.get("github_webhook_secret"):
        db_data["github_webhook_secret"] = settings.GITHUB_WEBHOOK_SECRET_DEFAULT

    db_project = Project(**db_data)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    logger.info(f"Project created: {db_project.id} ({project.repo_full_name})")
    return db_project


@router.get("/", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    """List all projects"""
    projects = db.query(Project).all()
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get project by ID"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectResponse, dependencies=[Depends(require_admin)])
def update_project(
    project_id: int,
    project: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """Update project (admin only)"""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = project.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    logger.info(f"Project updated: {project_id}")
    return db_project


@router.delete("/{project_id}", dependencies=[Depends(require_admin)])
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete project (admin only)"""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(db_project)
    db.commit()

    logger.info(f"Project deleted: {project_id}")
    return {"status": "deleted"}
