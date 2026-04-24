"""
VoteWise AI — Application Configuration
Uses pydantic-settings for environment variable management.
"""

import logging
import os
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict
from google.cloud import secretmanager

logger = logging.getLogger("votewise.config")

def get_secret_from_gcp(secret_id: str, default: str) -> str:
    """Fetch a secret from Google Cloud Secret Manager."""
    try:
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            logger.info("GOOGLE_CLOUD_PROJECT not set, skipping Secret Manager")
            return default
            
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logger.info(f"Could not fetch secret {secret_id} from Secret Manager: {e}")
        return default


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "VoteWise AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "info"

    # Google AI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-flash-latest"

    # Database
    DATABASE_PATH: str = "./votewise.db"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Cache
    CACHE_TTL_SECONDS: int = 86400  # 24 hours

    # Security
    MAX_MESSAGE_LENGTH: int = 2000
    RATE_LIMIT_PER_MINUTE: int = 30

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
