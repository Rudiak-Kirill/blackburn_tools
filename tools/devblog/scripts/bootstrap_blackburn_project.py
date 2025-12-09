#!/usr/bin/env python
"""
Bootstrap script to create or update the Blackburn DevBlog project.

This script:
1. Creates database if needed
2. Finds or creates Project record for Rudiak-Kirill/blackburn_tools
3. Sets up telegram_chat_id, ai_enabled, and other defaults
4. Generates a webhook secret if missing
5. Prints ready-to-use webhook configuration

Usage:
    python scripts/bootstrap_blackburn_project.py
"""
import sys
import secrets
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models import Project
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)


def bootstrap_blackburn_project():
    """Create or update Blackburn DevBlog project."""
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ensured")
    
    db = SessionLocal()
    
    try:
        # Configuration for Blackburn Tools project
        repo_full_name = "Rudiak-Kirill/blackburn_tools"
        project_name = "Blackburn DevBlog"
        telegram_chat_id = "@blackburn_devblog"  # Public channel; could also be -100... for private
        
        # Try to find existing project
        project = db.query(Project).filter(
            Project.repo_full_name == repo_full_name
        ).first()
        
        if project:
            logger.info(f"Found existing project: {project.name} (ID: {project.id})")
            
            # Update fields
            project.name = project_name
            project.telegram_chat_id = telegram_chat_id
            project.ai_enabled = True  # Enable AI by default for better posts
            project.language = "ru"
            
            # Generate secret if missing
            if not project.github_webhook_secret:
                project.github_webhook_secret = secrets.token_hex(16)
                logger.info("Generated new webhook secret")
            
            db.add(project)
            db.commit()
            logger.info(f"Updated project: {project_name}")
        else:
            logger.info(f"Creating new project: {project_name}")
            
            project = Project(
                name=project_name,
                repo_type="github",
                repo_full_name=repo_full_name,
                github_webhook_secret=secrets.token_hex(16),
                language="ru",
                ai_enabled=True,
                post_mode="per_push",
                telegram_chat_id=telegram_chat_id,
            )
            db.add(project)
            db.commit()
            db.refresh(project)
            logger.info(f"Created project: {project_name} (ID: {project.id})")
        
        # Print configuration
        print("\n" + "="*70)
        print("✅ Blackburn DevBlog Project Bootstrap Complete")
        print("="*70)
        print(f"Project Name:        {project.name}")
        print(f"Project ID:          {project.id}")
        print(f"Repository:          {project.repo_full_name}")
        print(f"Telegram Chat ID:    {project.telegram_chat_id}")
        print(f"AI Enabled:          {project.ai_enabled}")
        print(f"Language:            {project.language}")
        print()
        print("GitHub Webhook Configuration:")
        print("-" * 70)
        print(f"Webhook Secret:      {project.github_webhook_secret}")
        print()
        print("Next steps:")
        print("1. Start the DevBlog server: python main.py")
        print("2. Configure GitHub Webhook in your repository settings:")
        print(f"   - Payload URL: https://<your-domain>/webhook/github")
        print(f"   - Content type: application/json")
        print(f"   - Secret: {project.github_webhook_secret}")
        print(f"   - Events: Push events only")
        print("3. Make a test commit to trigger the webhook")
        print("="*70 + "\n")
        
    finally:
        db.close()


if __name__ == "__main__":
    try:
        bootstrap_blackburn_project()
    except Exception as e:
        logger.exception("Bootstrap failed")
        print(f"\n❌ Error: {e}\n", file=sys.stderr)
        sys.exit(1)
