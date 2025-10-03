from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AnyUrl, model_validator

class Settings(BaseSettings):
    # Env identity (support both names)
    APP_ENV: str = Field(default="dev")   # dev | staging | prod
    ENV: str = Field(default="dev")       # legacy name used elsewhere

    # Logging
    LOG_LEVEL: str = Field(default="INFO")

    # Features / Limits
    MAX_FILE_MB: int = Field(default=10)
    RATE_LIMIT_RPS: int = Field(default=2)
    RATE_LIMIT_PER_MIN: int = Field(default=60)
    RATE_LIMIT_PER_DAY: int = Field(default=1000)

    # Billing / integrations
    BILLING_PROVIDER: str = Field(default="none")
    VT_API_KEY: Optional[str] = None

    # Core infrastructure
    DATABASE_URL: AnyUrl
    REDIS_URL: AnyUrl

    # Security secrets
    ADMIN_KEY: str = Field(min_length=8)
    KEY_PEPPER: str = Field(min_length=16)

    # CORS
    CORS_ALLOW_ORIGINS: str = Field(default="")

    @property
    def cors_origins(self) -> List[str]:
        s = (self.CORS_ALLOW_ORIGINS or "").strip()
        return [o.strip() for o in s.split(",")] if s else []

    # Read .env in dev; Render uses process env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Keep ENV and APP_ENV synchronized (either name can be set)
    @model_validator(mode="after")
    def _sync_env_names(self):
        # prefer explicit APP_ENV if user set both
        if not self.ENV:
            object.__setattr__(self, "ENV", self.APP_ENV)
        if not self.APP_ENV:
            object.__setattr__(self, "APP_ENV", self.ENV)
        return self

@lru_cache
def get_settings() -> Settings:
    return Settings()