"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Application
    APP_ENV: str = "dev"
    SECRET_KEY: str = "dev-secret-key"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./blackburn_tools.db"
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    
    # GitHub
    GITHUB_WEBHOOK_SECRET_DEFAULT: str = "test-secret"
    # Admin API key for protecting admin endpoints
    ADMIN_API_KEY: Optional[str] = None
    # Telegram rate limit (messages per minute). 0 disables limiter.
    TELEGRAM_RATE_LIMIT_PER_MIN: int = 20
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
