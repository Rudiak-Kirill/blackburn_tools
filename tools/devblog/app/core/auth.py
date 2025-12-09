"""
Admin auth utilities
"""
from fastapi import Header, HTTPException
from typing import Optional

from app.core.config import settings


def require_admin(x_admin_token: Optional[str] = Header(None, alias="X-Admin-Token")):
    """Dependency that enforces presence of valid admin API key in header `X-Admin-Token`"""
    if not settings.ADMIN_API_KEY:
        # In case no admin key is set, deny by default
        raise HTTPException(status_code=403, detail="Admin API key not configured")
    if not x_admin_token or x_admin_token != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin API token")
    return True
