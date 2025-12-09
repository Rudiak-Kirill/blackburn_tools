#!/usr/bin/env python
"""
Print GitHub webhook configuration for a project.

This script displays the Payload URL and Secret needed to configure
GitHub Webhook in your repository settings.

Usage:
    python scripts/print_webhook_instructions.py [--project-id ID]
"""
import sys
import argparse
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models import Project
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)


def print_webhook_instructions(project_id: int = None):
    """Print webhook configuration for a project."""
    
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        if project_id:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                print(f"❌ Project with ID {project_id} not found\n", file=sys.stderr)
                return False
        else:
            # Find Blackburn project by default
            project = db.query(Project).filter(
                Project.repo_full_name == "Rudiak-Kirill/blackburn_tools"
            ).first()
            
            if not project:
                # List available projects
                projects = db.query(Project).all()
                if not projects:
                    print("❌ No projects found. Run bootstrap_blackburn_project.py first.\n", file=sys.stderr)
                    return False
                
                print("Available projects:")
                for p in projects:
                    print(f"  ID {p.id}: {p.name} ({p.repo_full_name})")
                print()
                return False
        
        # Print webhook configuration
        print("\n" + "="*70)
        print(f"📋 GitHub Webhook Configuration for: {project.name}")
        print("="*70)
        print()
        print("1. Go to your GitHub repository settings")
        print("   URL: https://github.com/{}/settings/hooks".format(project.repo_full_name))
        print()
        print("2. Click 'Add webhook'")
        print()
        print("3. Fill in these values:")
        print()
        print("   Payload URL:")
        print(f"   https://<your-domain-or-ngrok-url>/webhook/github")
        print()
        print("   Content type:")
        print("   application/json")
        print()
        print("   Secret:")
        print(f"   {project.github_webhook_secret}")
        print()
        print("   Which events would you like to trigger this webhook?")
        print("   ✓ Push events (select only this)")
        print()
        print("   Active:")
        print("   ✓ Enabled")
        print()
        print("="*70)
        print()
        print("📝 For local testing with ngrok:")
        print("   1. Install ngrok: https://ngrok.com")
        print("   2. Run: ngrok http 8000")
        print("   3. Use the https URL in Payload URL above")
        print("   4. Test with: python scripts/simulate_webhook_blackburn.py")
        print()
        print("="*70 + "\n")
        
        return True
        
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Print GitHub webhook configuration"
    )
    parser.add_argument(
        "--project-id",
        type=int,
        default=None,
        help="Project ID (default: Blackburn DevBlog)"
    )
    
    args = parser.parse_args()
    
    try:
        success = print_webhook_instructions(args.project_id)
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.exception("Failed to print instructions")
        print(f"\n❌ Error: {e}\n", file=sys.stderr)
        sys.exit(1)
