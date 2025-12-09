"""
OpenAI integration for generating post content using gpt-4o-mini
"""
import requests
from typing import List, Tuple, Optional

from app.core.config import settings
from app.models import CommitEvent, Project
from app.core.logger import get_logger

logger = get_logger(__name__)


class OpenAIService:
    """Simple OpenAI wrapper using HTTP requests to Responses API.

    This avoids hard dependency on openai package and keeps code explicit.
    """

    API_URL = "https://api.openai.com/v1/responses"

    def __init__(self, project: Project):
        self.project = project
        self.api_key = settings.OPENAI_API_KEY
        self.model = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")
        self.timeout = 20

    def _build_prompt(self, commits: List[CommitEvent]) -> str:
        # Compose a compact prompt describing commits for a short Telegram post.
        lines = []
        lines.append(f"Create a short Telegram post (max 250 tokens) in {self.project.language} for the project '{self.project.name}'.")
        lines.append("Output should be a single message suitable for Telegram, include a short title, 2-6 bullet points summarizing commits, appropriate emoji, and 2-4 hashtags. Use HTML formatting for bold and italics where helpful.")
        lines.append("Tone: concise, friendly, developer-focused. If commit messages are trivial, summarize them. Do not invent features.")
        lines.append("---")
        for c in commits:
            when = c.pushed_at.isoformat() if getattr(c, "pushed_at", None) else ""
            lines.append(f"- {c.commit_hash[:7]} | {c.author} | {when} | {c.message.splitlines()[0]}")

        return "\n".join(lines)

    def generate_post(self, commits: List[CommitEvent]) -> Tuple[bool, Optional[str]]:
        if not self.api_key:
            return False, "OpenAI API key not configured"

        prompt = self._build_prompt(commits)

        payload = {
            "model": self.model,
            "input": prompt,
            "max_output_tokens": 500,
            "temperature": 0.2,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            resp = requests.post(self.API_URL, json=payload, headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            # Responses API may return choices or output; try to extract text
            # New API: data['output'] is list of dicts with 'content' or 'text'
            text = None
            if isinstance(data.get("output"), list) and data.get("output"):
                parts = []
                for item in data.get("output"):
                    # item can be dict with 'content' which may be list/dict
                    if isinstance(item, dict):
                        if "content" in item:
                            if isinstance(item["content"], list):
                                for c in item["content"]:
                                    if isinstance(c, dict) and c.get("text"):
                                        parts.append(c.get("text"))
                            elif isinstance(item["content"], str):
                                parts.append(item["content"])
                        elif item.get("text"):
                            parts.append(item.get("text"))
                    elif isinstance(item, str):
                        parts.append(item)

                text = "\n".join(parts).strip() if parts else None

            # Fallback to top-level 'output_text' or choices
            if not text:
                text = data.get("output_text") or data.get("choices", [{}])[0].get("message", {}).get("content", "")

            if not text:
                return False, "OpenAI returned empty response"

            return True, text

        except requests.RequestException as exc:
            logger.error(f"OpenAI request failed: {exc}")
            return False, str(exc)
