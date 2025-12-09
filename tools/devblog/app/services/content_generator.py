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

    def _template_from_commits(self, commits: List[CommitEvent]) -> str:
        if not commits:
            return ""

        commits_text = ""
        for commit in commits:
            message = commit.message.split("\n")[0]
            commits_text += f"• {message}\n"

        if self.project.language == "ru":
            template = f"""🛠 <b>Обновление: {self.project.name}</b>

📅 {datetime.utcnow().strftime('%d.%m.%Y %H:%M')}

<b>Изменения:</b>
{commits_text.strip()}

#devlog #update"""
        else:
            template = f"""🛠 <b>Update: {self.project.name}</b>

📅 {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}

<b>Changes:</b>
{commits_text.strip()}

#devlog #update"""

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
