"""
SQLAlchemy models
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base


class Project(Base):
    """Project model"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    repo_type = Column(String(50), default="github", nullable=False)  # "github"
    repo_full_name = Column(String(255), nullable=False, unique=True)  # "owner/repo"
    github_webhook_secret = Column(String(255), nullable=True)
    language = Column(String(10), default="ru")  # "ru", "en"
    ai_enabled = Column(Boolean, default=False)
    post_mode = Column(String(50), default="per_push")  # "per_push", "daily_digest"
    telegram_chat_id = Column(String(255), nullable=False)
    telegram_bot_token = Column(String(255), nullable=True)  # if custom per-project
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    posts = relationship("Post", back_populates="project", cascade="all, delete-orphan")
    commit_events = relationship("CommitEvent", back_populates="project", cascade="all, delete-orphan")


class CommitEvent(Base):
    """Commit event model - raw data from GitHub"""
    __tablename__ = "commit_events"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    commit_hash = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    pushed_at = Column(DateTime, nullable=False)
    branch = Column(String(255), nullable=False)
    data_raw = Column(JSON, nullable=True)  # Full GitHub webhook payload
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="commit_events")


class Post(Base):
    """Published post model"""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    source = Column(String(50), default="github", nullable=False)  # "github"
    content = Column(Text, nullable=False)  # The actual message sent
    content_md = Column(Text, nullable=True)  # Markdown version for website
    status = Column(String(50), default="success")  # "success", "error"
    error_message = Column(Text, nullable=True)
    telegram_message_id = Column(String(255), nullable=True)  # For tracking in Telegram
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="posts")
