#!/usr/bin/env python
"""
Simulate a GitHub push webhook for Blackburn Tools repository.

This script creates a realistic GitHub push webhook payload and sends it to 
your local FastAPI server with the correct HMAC-SHA256 signature.

Usage:
    python scripts/simulate_webhook_blackburn.py [--num-commits N]
"""
import sys
import json
import hmac
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
import requests

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models import Project
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)


def generate_github_webhook_payload(num_commits: int = 3) -> dict:
    """Generate a realistic GitHub push webhook payload."""
    
    # Get Blackburn project to find its secret
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        project = db.query(Project).filter(
            Project.repo_full_name == "Rudiak-Kirill/blackburn_tools"
        ).first()
        
        if not project:
            print("❌ Blackburn project not found. Run bootstrap_blackburn_project.py first.\n", 
                  file=sys.stderr)
            return None, None
        
        webhook_secret = project.github_webhook_secret
        
    finally:
        db.close()
    
    # Generate commit objects
    commits = []
    for i in range(num_commits):
        commit = {
            "id": f"{'a' * (40 - len(str(i)))}{i}",
            "tree_id": "f" * 40,
            "distinct": True,
            "message": f"feat: add awesome feature #{i+1}\n\nThis is a detailed description of the feature.",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "url": f"https://github.com/Rudiak-Kirill/blackburn_tools/commit/{'a' * (40 - len(str(i)))}{i}",
            "author": {
                "name": "Kirill Rudyak",
                "email": "kirill@example.com",
                "username": "Rudiak-Kirill"
            },
            "committer": {
                "name": "Kirill Rudyak",
                "email": "kirill@example.com",
                "username": "Rudiak-Kirill"
            },
            "added": ["file1.py"],
            "removed": [],
            "modified": ["README.md"]
        }
        commits.append(commit)
    
    payload = {
        "ref": "refs/heads/main",
        "before": "0" * 40,
        "after": commits[0]["id"] if commits else ("1" * 40),
        "repository": {
            "id": 123456789,
            "node_id": "MDEwOlJlcG9zaXRvcnk...",
            "name": "blackburn_tools",
            "full_name": "Rudiak-Kirill/blackburn_tools",
            "private": False,
            "owner": {
                "name": "Rudiak-Kirill",
                "email": "kirill@example.com",
                "login": "Rudiak-Kirill",
                "id": 123456,
            },
            "html_url": "https://github.com/Rudiak-Kirill/blackburn_tools",
            "description": "Advanced tools and utilities collection",
            "url": "https://github.com/Rudiak-Kirill/blackburn_tools",
            "created_at": 1609459200,
            "updated_at": int(datetime.utcnow().timestamp()),
            "pushed_at": int(datetime.utcnow().timestamp()),
            "git_url": "git://github.com/Rudiak-Kirill/blackburn_tools.git",
            "ssh_url": "git@github.com:Rudiak-Kirill/blackburn_tools.git",
            "clone_url": "https://github.com/Rudiak-Kirill/blackburn_tools.git",
            "svn_url": "https://svn.github.com/Rudiak-Kirill/blackburn_tools",
            "homepage": "https://example.com",
            "size": 2048,
            "stargazers_count": 10,
            "watchers_count": 10,
            "language": "Python",
            "has_issues": True,
            "has_projects": True,
            "has_downloads": True,
            "has_wiki": True,
            "has_pages": False,
            "forks_count": 0,
            "open_issues_count": 0,
            "default_branch": "main"
        },
        "pusher": {
            "name": "Rudiak-Kirill",
            "email": "kirill@example.com"
        },
        "sender": {
            "login": "Rudiak-Kirill",
            "id": 123456,
            "avatar_url": "https://avatars.githubusercontent.com/u/123456?v=4",
            "type": "User"
        },
        "created": False,
        "deleted": False,
        "forced": False,
        "compare": "https://github.com/Rudiak-Kirill/blackburn_tools/compare/0000000...aaaaaaa",
        "commits": commits,
        "head_commit": commits[0] if commits else None
    }
    
    return payload, webhook_secret


def send_webhook(payload: dict, webhook_secret: str, server_url: str = "http://localhost:8000"):
    """Send webhook to local server with correct signature."""
    
    # Compute HMAC-SHA256 signature
    payload_json = json.dumps(payload, separators=(',', ':'))
    signature = hmac.new(
        webhook_secret.encode(),
        payload_json.encode(),
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": f"sha256={signature}",
        "X-GitHub-Event": "push",
        "X-GitHub-Delivery": "12345-67890"
    }
    
    webhook_url = f"{server_url}/webhook/github"
    
    print("\n" + "="*70)
    print("📨 Sending GitHub Webhook Simulation")
    print("="*70)
    print(f"URL:                 {webhook_url}")
    print(f"Commits:             {len(payload.get('commits', []))}")
    print(f"Repository:          {payload['repository']['full_name']}")
    print(f"Branch:              {payload['ref'].split('/')[-1]}")
    print()
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers=headers,
            timeout=10
        )
        
        print(f"Response Status:     {response.status_code}")
        print()
        
        if response.status_code == 200:
            print("✅ Webhook received successfully!")
            print()
            try:
                response_data = response.json()
                print("Response Data:")
                print(json.dumps(response_data, indent=2, ensure_ascii=False))
            except:
                print("Response:", response.text)
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            print("Response:", response.text)
        
        print()
        print("="*70)
        print("💡 Check the server logs for detailed processing information")
        print("="*70 + "\n")
        
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server at {}".format(server_url))
        print()
        print("Make sure the DevBlog server is running:")
        print("  python main.py")
        print()
        return False
    except Exception as e:
        print(f"❌ Error sending webhook: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Simulate a GitHub push webhook"
    )
    parser.add_argument(
        "--num-commits",
        type=int,
        default=3,
        help="Number of commits to simulate (default: 3)"
    )
    parser.add_argument(
        "--server-url",
        type=str,
        default="http://localhost:8000",
        help="Server URL (default: http://localhost:8000)"
    )
    
    args = parser.parse_args()
    
    try:
        payload, webhook_secret = generate_github_webhook_payload(args.num_commits)
        
        if payload and webhook_secret:
            success = send_webhook(payload, webhook_secret, args.server_url)
            sys.exit(0 if success else 1)
        else:
            sys.exit(1)
            
    except Exception as e:
        logger.exception("Webhook simulation failed")
        print(f"\n❌ Error: {e}\n", file=sys.stderr)
        sys.exit(1)
