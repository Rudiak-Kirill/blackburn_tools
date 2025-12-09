"""
FastAPI application factory
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import Base, engine
from app.api import api_router
from app.core.logger import get_logger
from app import __version__

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
    
    app = FastAPI(
        title="Blackburn Tools",
        description="Auto Content Publisher - Dev Blog Generator",
        version=__version__,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(api_router)
    
    @app.on_event("startup")
    async def startup_event():
        logger.info("Application starting up...")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Application shutting down...")
    
    return app


app = create_app()
