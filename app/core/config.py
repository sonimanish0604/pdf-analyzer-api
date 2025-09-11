# app/core/config.py
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AnyUrl, validator

class Settings(BaseSettings):
    # Env identity
    APP_ENV: str = Field(default="dev")  # dev | staging | prod

    # Logging
    LOG_LEVEL: str = Field(default="INFO")

    # Features / Limits
    MAX_FILE_MB: int = Field(default=10)
    RATE_LIMIT_RPS: int = Field(default=2)
    BILLING_PROVIDER: str = Field(default="none")  # none | rapidapi | stripe

    # Integrations
    VT_API_KEY: Optional[str] = None
    DATABASE_URL: Optional[AnyUrl] = None
    REDIS_URL: Optional[AnyUrl] = None

    # CORS (comma-separated)
    CORS_ALLOW_ORIGINS: str = Field(default="")

    @property
    def cors_origins(self) -> List[str]:
        s = (self.CORS_ALLOW_ORIGINS or "").strip()
        return [o.strip() for o in s.split(",")] if s else []

    # Only load .env automatically in dev
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

@lru_cache
def get_settings() -> Settings:
    """
    Cached settings so all imports share one object.
    In dev, reads .env. In staging/prod, app just reads process env vars.
    """
    return Settings()
