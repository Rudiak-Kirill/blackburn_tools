"""
API routers initialization
"""
from fastapi import APIRouter
from .health import router as health_router
from .webhook import router as webhook_router
from .projects import router as projects_router
from .admin import router as admin_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(webhook_router)
api_router.include_router(projects_router)
api_router.include_router(admin_router)

__all__ = ["api_router"]
