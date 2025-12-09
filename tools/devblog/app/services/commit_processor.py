"""
Commit processing service
Filters, validates and prepares commits for publishing
"""
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
import re

from app.models import Project, CommitEvent, Post
from app.core.logger import get_logger
from app.integrations.telegram import TelegramService
from app.services.content_generator import ContentGenerator

logger = get_logger(__name__)


class CommitProcessor:
    """Process GitHub webhook commits and send to Telegram"""
    
    def __init__(self, db: Session, project: Project):
        self.db = db
        self.project = project
        self.telegram = TelegramService(project)
        self.generator = ContentGenerator(project)
    
    def process_webhook_commits(
        self,
        commits: List[Dict[str, Any]],
        branch: str
    ) -> Dict[str, Any]:
        """
        Process webhook commits:
        1. Save all commits to DB
        2. Filter by branch and prefixes
        3. Generate message
        4. Send to Telegram
        """
        if not commits:
            return {"processed": 0, "message_sent": False}
        
        # Save raw commits to DB
        saved_commits = []
        for commit_data in commits:
            try:
                # Parse timestamp robustly (GitHub may provide Z timezone)
                ts = commit_data.get("timestamp") or datetime.utcnow().isoformat()
                if isinstance(ts, str) and ts.endswith("Z"):
                    ts = ts.replace("Z", "+00:00")
                try:
                    pushed_at = datetime.fromisoformat(ts)
                except Exception:
                    pushed_at = datetime.utcnow()

                commit_event = CommitEvent(
                    project_id=self.project.id,
                    commit_hash=commit_data.get("id", "")[:40],
                    author=commit_data.get("author", {}).get("name", "Unknown"),
                    message=commit_data.get("message", ""),
                    pushed_at=pushed_at,
                    branch=branch,
                    data_raw=commit_data,
                )
                self.db.add(commit_event)
                saved_commits.append(commit_event)
            except Exception as e:
                logger.error(f"Error saving commit: {e}")
        
        self.db.commit()
        
        # Filter commits by rules
        filtered_commits = self._filter_commits(saved_commits)
        
        if not filtered_commits:
            logger.info(f"No commits passed filters for project {self.project.id}")
            return {"processed": len(saved_commits), "message_sent": False}
        
        # Generate content
        message_text = self.generator.generate_from_commits(filtered_commits)
        
        # Send to Telegram
        try:
            telegram_result = self.telegram.send_message(message_text)
            
            # Save post to DB
            post = Post(
                project_id=self.project.id,
                source="github",
                content=message_text,
                status="success" if telegram_result["success"] else "error",
                error_message=telegram_result.get("error"),
                telegram_message_id=telegram_result.get("message_id"),
            )
            self.db.add(post)
            self.db.commit()
            
            return {
                "processed": len(saved_commits),
                "filtered": len(filtered_commits),
                "message_sent": telegram_result["success"]
            }
        except Exception as e:
            logger.error(f"Error sending to Telegram: {e}")
            
            post = Post(
                project_id=self.project.id,
                source="github",
                content=message_text,
                status="error",
                error_message=str(e),
            )
            self.db.add(post)
            self.db.commit()
            
            return {
                "processed": len(saved_commits),
                "filtered": len(filtered_commits),
                "message_sent": False,
                "error": str(e)
            }
    
    def _filter_commits(self, commits: List[CommitEvent]) -> List[CommitEvent]:
        """
        Filter commits by rules:
        - Branch matching (if configured)
        - Prefix matching (feat:, fix:, chore:, etc.)
        """
        filtered = []
        
        # Prefixes to include (configurable, default includes main types)
        allowed_prefixes = [
            "feat:", "feature:",
            "fix:", "bugfix:",
            "perf:", "performance:",
            "docs:", "doc:",
            "style:",
            "refactor:",
            "test:",
            "chore:",
        ]
        
        for commit in commits:
            message = commit.message.strip()
            
            # Check if message starts with allowed prefix
            has_prefix = any(message.lower().startswith(prefix) for prefix in allowed_prefixes)
            
            # Also include commits that have a commit hash pattern in first line
            # (some workflows don't use prefixes)
            if has_prefix or len(message) > 10:
                filtered.append(commit)
                logger.debug(f"Commit included: {commit.commit_hash} - {message[:50]}")
            else:
                logger.debug(f"Commit filtered out: {commit.commit_hash} - {message[:50]}")
        
        return filtered
