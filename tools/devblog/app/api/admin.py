"""Admin HTML views for managing Projects (minimal)
"""
from typing import Optional
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Project
from app.core.config import settings

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


def admin_guard(request: Request):
    """Allow access if no ADMIN_API_KEY is set; otherwise require X-Admin-Token header or query param admin_token."""
    if not settings.ADMIN_API_KEY:
        return True
    token = request.headers.get("X-Admin-Token") or request.query_params.get("admin_token")
    if not token or token != settings.ADMIN_API_KEY:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid admin token")
    return True


@router.get("/projects")
def projects_list(request: Request, db: Session = Depends(get_db), _: bool = Depends(admin_guard)):
    projects = db.query(Project).order_by(Project.id).all()
    return templates.TemplateResponse("admin/projects_list.html", {"request": request, "projects": projects})


@router.get("/projects/create")
def projects_create_form(request: Request, _: bool = Depends(admin_guard)):
    return templates.TemplateResponse("admin/project_form.html", {"request": request, "action": "create", "project": None})


@router.post("/projects/create")
def projects_create(request: Request, name: str = Form(...), repo_full_name: str = Form(...), telegram_chat_id: str = Form(...), language: str = Form("ru"), ai_enabled: Optional[str] = Form(None), db: Session = Depends(get_db), _: bool = Depends(admin_guard)):
    ai_flag = bool(ai_enabled)
    p = Project(name=name, repo_full_name=repo_full_name, telegram_chat_id=telegram_chat_id, language=language, ai_enabled=ai_flag)
    db.add(p)
    db.commit()
    return RedirectResponse(url="/admin/projects", status_code=303)


@router.get("/projects/{project_id}/edit")
def projects_edit_form(request: Request, project_id: int, db: Session = Depends(get_db), _: bool = Depends(admin_guard)):
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")
    return templates.TemplateResponse("admin/project_form.html", {"request": request, "action": "edit", "project": p})


@router.post("/projects/{project_id}/edit")
def projects_edit(request: Request, project_id: int, name: str = Form(None), language: str = Form(None), ai_enabled: Optional[str] = Form(None), post_mode: str = Form(None), telegram_chat_id: str = Form(None), db: Session = Depends(get_db), _: bool = Depends(admin_guard)):
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")
    if name:
        p.name = name
    if language:
        p.language = language
    if ai_enabled is not None:
        p.ai_enabled = bool(ai_enabled)
    if post_mode:
        p.post_mode = post_mode
    if telegram_chat_id:
        p.telegram_chat_id = telegram_chat_id
    db.add(p)
    db.commit()
    return RedirectResponse(url="/admin/projects", status_code=303)


@router.post("/projects/{project_id}/toggle-ai")
def projects_toggle_ai(project_id: int, db: Session = Depends(get_db), _: bool = Depends(admin_guard)):
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")
    p.ai_enabled = not p.ai_enabled
    db.add(p)
    db.commit()
    return RedirectResponse(url="/admin/projects", status_code=303)


@router.post("/projects/{project_id}/delete")
def projects_delete(project_id: int, db: Session = Depends(get_db), _: bool = Depends(admin_guard)):
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(p)
    db.commit()
    return RedirectResponse(url="/admin/projects", status_code=303)
