"""
Telegram Bot integration service
"""
import requests
import time
from typing import Dict, Any, Optional

from app.models import Project
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class TelegramService:
    """Telegram Bot API integration with simple in-memory rate limiting (token-bucket).

    Notes:
    - Limiter is per-chat_id and in-memory (single-process). For multi-process or multi-host
      deployments use Redis or another central store.
    - Configure `TELEGRAM_RATE_LIMIT_PER_MIN` in environment (0 disables limiter).
    """
    TELEGRAM_API_BASE = "https://api.telegram.org"
    SEND_MESSAGE_ENDPOINT = "/sendMessage"

    # In-memory token buckets: {chat_id: {tokens: float, last_refill: float}}
    _buckets: Dict[str, Dict[str, float]] = {}
    
    def __init__(self, project: Project):
        self.project = project
        # Use project-specific token if available, otherwise use global
        self.bot_token = project.telegram_bot_token or settings.TELEGRAM_BOT_TOKEN
        self.chat_id = project.telegram_chat_id
        # rate limit per minute
        self.rate_per_min = max(0, int(settings.TELEGRAM_RATE_LIMIT_PER_MIN or 0))

    def _allow_send(self) -> tuple[bool, Optional[float]]:
        """Check and update token bucket for the chat.

        Returns (allowed, retry_after_seconds)
        """
        if self.rate_per_min <= 0:
            return True, None

        now = time.time()
        key = str(self.chat_id)
        bucket = self._buckets.get(key)
        # Refill rate per second
        rate_per_sec = self.rate_per_min / 60.0
        capacity = float(self.rate_per_min)

        if not bucket:
            # initialize with full capacity minus one token for immediate send
            self._buckets[key] = {"tokens": capacity - 1.0, "last_refill": now}
            return True, None

        # refill tokens
        elapsed = now - bucket["last_refill"]
        refill = elapsed * rate_per_sec
        tokens = min(capacity, bucket["tokens"] + refill)

        if tokens >= 1.0:
            bucket["tokens"] = tokens - 1.0
            bucket["last_refill"] = now
            self._buckets[key] = bucket
            return True, None
        else:
            # compute retry-after in seconds
            needed = 1.0 - tokens
            retry_after = needed / rate_per_sec if rate_per_sec > 0 else None
            return False, retry_after

    def send_message(self, text: str, parse_mode: str = "HTML") -> Dict[str, Any]:
        """
        Send message to Telegram
        
        Returns:
            {
                "success": bool,
                "message_id": Optional[str],
                "error": Optional[str]
            }
        """
        if not self.bot_token:
            error = "Telegram bot token not configured"
            logger.error(error)
            return {
                "success": False,
                "error": error
            }

        # Rate limiting check
        allowed, retry = self._allow_send()
        if not allowed:
            error = f"Rate limit exceeded. Retry after {int(retry)}s" if retry else "Rate limit exceeded"
            logger.warning(error)
            return {"success": False, "error": error}
        
        url = f"{self.TELEGRAM_API_BASE}/bot{self.bot_token}{self.SEND_MESSAGE_ENDPOINT}"
        
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True,
        }
        
        try:
            logger.info(f"Sending message to Telegram for project {self.project.id}")
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    message_id = str(data.get("result", {}).get("message_id"))
                    logger.info(f"Message sent successfully: {message_id}")
                    return {
                        "success": True,
                        "message_id": message_id,
                    }
                else:
                    error = data.get("description", "Unknown Telegram error")
                    logger.error(f"Telegram API error: {error}")
                    return {
                        "success": False,
                        "error": error
                    }
            else:
                error = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"Telegram request failed: {error}")
                return {
                    "success": False,
                    "error": error
                }
        
        except requests.exceptions.Timeout:
            error = "Telegram request timeout"
            logger.error(error)
            return {
                "success": False,
                "error": error
            }
        except requests.exceptions.RequestException as e:
            error = f"Request error: {str(e)}"
            logger.error(error)
            return {
                "success": False,
                "error": error
            }
        except Exception as e:
            error = f"Unexpected error: {str(e)}"
            logger.error(error)
            return {
                "success": False,
                "error": error
            }
