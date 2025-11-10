"""Application configuration using pydantic settings."""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the PGIP backend."""

    api_v1_prefix: str = "/api/v1"
    project_name: str = "PanGenome Insight Platform"
    description: str = (
        "Open-source platform for interpreting variation across linear "
        "and graph-based references."
    )
    allowed_origins: List[str] = ["*"]
    docs_url: str = "/docs"
    openapi_url: str = "/openapi.json"
    database_url: str = "sqlite+aiosqlite:///./pgip.db"
    database_echo: bool = False
    seed_demo_data: bool = True

    model_config = SettingsConfigDict(env_prefix="PGIP_", env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """Return a cached instance of settings."""

    return Settings()
