"""Application settings and configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = Field(default="areamedica-api")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    environment: str = Field(default="production")

    # Database
    database_url: str = Field(..., description="Database connection URL")
    database_pool_size: int = Field(default=20)
    database_max_overflow: int = Field(default=30)

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")
    cache_ttl: int = Field(default=300)

    # Authentication
    secret_key: str = Field(..., description="Secret key for JWT token generation")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)

    # Banesco
    banesco_api_url: str = Field(..., description="Banesco API base URL")
    banesco_api_key: str = Field(..., description="Banesco API key")
    banesco_timeout: int = Field(default=30)
    banesco_rate_limit: int = Field(default=2)

    # Monitoring
    log_level: str = Field(default="INFO")
    sentry_dsn: str = Field(default="")

    # CORS
    allowed_origins: List[str] = Field(default=["*"])
    allowed_methods: List[str] = Field(default=["GET", "POST", "PUT", "DELETE"])
    allowed_headers: List[str] = Field(default=["*"])

    # Rate Limiting
    rate_limit_requests: int = Field(default=100)
    rate_limit_period: int = Field(default=3600)

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
