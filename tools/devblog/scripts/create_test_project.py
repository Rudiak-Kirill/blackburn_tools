"""
Create a test project directly in the database for local E2E testing
"""
from app.db import Base, engine
from app.db.session import SessionLocal
from app.models import Project
from app.core.config import settings


def create_project():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        repo_full_name = "test_owner/test_repo"
        existing = db.query(Project).filter(Project.repo_full_name == repo_full_name).first()
        if existing:
            print(f"Project already exists: id={existing.id}, repo={existing.repo_full_name}")
            return

        project = Project(
            name="Test Project",
            repo_type="github",
            repo_full_name=repo_full_name,
            github_webhook_secret=settings.GITHUB_WEBHOOK_SECRET_DEFAULT or "test-secret",
            language="en",
            ai_enabled=False,
            post_mode="per_push",
            telegram_chat_id="123456789",
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        print(f"Created project: id={project.id}, repo={project.repo_full_name}, secret={project.github_webhook_secret}")
    finally:
        db.close()


if __name__ == "__main__":
    create_project()
