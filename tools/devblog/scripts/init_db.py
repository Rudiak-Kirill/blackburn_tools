"""
Initialize database and create tables
"""
from app.db import Base, engine
from app.models import Project, CommitEvent, Post
from app.core.logger import get_logger

logger = get_logger(__name__)


def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")


if __name__ == "__main__":
    init_db()
