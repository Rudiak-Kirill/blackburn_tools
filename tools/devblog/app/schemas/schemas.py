"""
Pydantic schemas for request/response validation
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


# Project Schemas
class ProjectBase(BaseModel):
    """Base project schema"""
    name: str = Field(..., min_length=1, max_length=255)
    repo_type: str = "github"
    repo_full_name: str = Field(..., min_length=1, max_length=255)
    github_webhook_secret: Optional[str] = None
    language: str = "ru"
    ai_enabled: bool = False
    post_mode: str = "per_push"
    telegram_chat_id: str = Field(..., min_length=1, max_length=255)
    telegram_bot_token: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Create project schema"""
    pass


class ProjectUpdate(BaseModel):
    """Update project schema"""
    name: Optional[str] = None
    language: Optional[str] = None
    ai_enabled: Optional[bool] = None
    post_mode: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    telegram_bot_token: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Project response schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# CommitEvent Schemas
class CommitEventBase(BaseModel):
    """Base commit event schema"""
    commit_hash: str
    author: str
    message: str
    pushed_at: datetime
    branch: str
    data_raw: Optional[dict] = None


class CommitEventCreate(CommitEventBase):
    """Create commit event schema"""
    project_id: int


class CommitEventResponse(CommitEventBase):
    """Commit event response schema"""
    id: int
    project_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Post Schemas
class PostBase(BaseModel):
    """Base post schema"""
    source: str = "github"
    content: str
    content_md: Optional[str] = None
    status: str = "success"
    error_message: Optional[str] = None
    telegram_message_id: Optional[str] = None


class PostCreate(PostBase):
    """Create post schema"""
    project_id: int


class PostResponse(PostBase):
    """Post response schema"""
    id: int
    project_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Health check response
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    environment: str


# GitHub Webhook payload (simplified)
class GitHubCommit(BaseModel):
    """GitHub commit payload"""
    id: str
    message: str
    author: dict
    timestamp: str
    url: Optional[str] = None


class GitHubPushPayload(BaseModel):
    """GitHub push webhook payload"""
    ref: str
    repository: dict
    commits: List[dict]
    pusher: dict
