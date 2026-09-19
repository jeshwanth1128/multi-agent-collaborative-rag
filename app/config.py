from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    gemini_api_key: SecretStr = SecretStr("")
    gemini_model: str = "gemini-3.6-flash"
    environment: str = "development"
    qdrant_path: str = "./data/qdrant"
    qdrant_url: str = ""
    qdrant_api_key: SecretStr = SecretStr("")
    database_path: str = "./data/sample.db"
    backend_api_key: SecretStr = SecretStr("")
    synthesis_enabled: bool = True
    web_search_enabled: bool = True
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip().rstrip("/") for origin in self.cors_origins.split(",") if origin.strip()]

    def resolve_path(self, value: str) -> Path:
        path = Path(value).expanduser()
        return path if path.is_absolute() else PROJECT_ROOT / path

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
