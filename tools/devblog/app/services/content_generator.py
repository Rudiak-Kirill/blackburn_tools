"""
Content generation service
Generates Telegram messages from commits
"""
from typing import List
from datetime import datetime

from app.models import Project, CommitEvent
from app.core.logger import get_logger
from app.integrations.openai_service import OpenAIService

logger = get_logger(__name__)


class ContentGenerator:
    """Generate message content from commits. Uses OpenAI when enabled on project, otherwise falls back to template."""

    def __init__(self, project: Project):
        self.project = project

    def _get_commit_emoji(self, message: str) -> str:
        """Get appropriate emoji based on commit type."""
        msg_lower = message.lower()
        if "feat" in msg_lower or "feature" in msg_lower or "add" in msg_lower:
            return "✨"
        elif "fix" in msg_lower or "bug" in msg_lower:
            return "🐛"
        elif "docs" in msg_lower or "documentation" in msg_lower:
            return "📚"
        elif "perf" in msg_lower or "performance" in msg_lower or "optimize" in msg_lower:
            return "⚡"
        elif "refactor" in msg_lower:
            return "♻️"
        elif "test" in msg_lower:
            return "🧪"
        elif "chore" in msg_lower or "update" in msg_lower:
            return "🔧"
        else:
            return "📝"

    def _extract_commit_type(self, message: str) -> str:
        """Extract commit type prefix (feat:, fix:, etc) if present."""
        if ":" not in message:
            return ""
        
        prefix = message.split(":")[0].strip().lower()
        types = ["feat", "fix", "docs", "style", "refactor", "perf", "test", "chore"]
        
        if prefix in types:
            return f"[{prefix.upper()}] "
        return ""

    def _template_from_commits(self, commits: List[CommitEvent]) -> str:
        if not commits:
            return ""

        commits_text = ""
        for commit in commits:
            # Get first line of commit message
            message = commit.message.split("\n")[0].strip()
            
            # Extract type prefix
            commit_type = self._extract_commit_type(message)
            if commit_type:
                # Remove type prefix from message to avoid duplication
                message = message.split(":", 1)[1].strip()
            
            # Get emoji
            emoji = self._get_commit_emoji(commit.message)
            
            # Format line
            commits_text += f"{emoji} {commit_type}{message}\n"

        commit_count = len(commits)
        
        if self.project.language == "ru":
            commit_word = "коммит" if commit_count == 1 else "коммита" if commit_count < 5 else "коммитов"
            header = f"🚀 <b>Blackburn Tools</b> — {commit_count} {commit_word}"
            timestamp = datetime.utcnow().strftime('%d.%m.%Y в %H:%M')
            
            template = f"""{header}

{commits_text.strip()}

<i>{timestamp}</i>

#devblog #blackburn_tools"""
        else:
            commit_word = "commit" if commit_count == 1 else "commits"
            header = f"🚀 <b>Blackburn Tools</b> — {commit_count} {commit_word}"
            timestamp = datetime.utcnow().strftime('%Y-%m-%d at %H:%M')
            
            template = f"""{header}

{commits_text.strip()}

<i>{timestamp}</i>

#devblog #blackburn_tools"""

        return template

    def generate_from_commits(self, commits: List[CommitEvent]) -> str:
        """Generate content. If `ai_enabled` on project and OpenAI configured, use it with fallback to template."""
        if not commits:
            return ""

        if getattr(self.project, "ai_enabled", False):
            try:
                ai = OpenAIService(self.project)
                ok, result = ai.generate_post(commits)
                if ok and result:
                    return result
                else:
                    logger.warning(f"OpenAI generation failed or empty: {result}. Falling back to template.")
            except Exception as exc:
                logger.exception(f"OpenAI generation exception: {exc}. Falling back to template.")

        # Fallback
        return self._template_from_commits(commits)
