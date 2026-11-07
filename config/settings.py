"""Application settings and environment configuration."""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for India Finance Intelligence Terminal."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Storage Backend: 'local' (file-based lakehouse) or 's3' (MinIO / AWS S3)
    STORAGE_BACKEND: str = "local"
    LAKEHOUSE_BASE_PATH: Path = Path("./data/lakehouse")

    # MinIO / S3 Settings
    MINIO_ENDPOINT: str = "http://localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    S3_RAW_BUCKET: str = "lakehouse-raw"
    S3_STAGING_BUCKET: str = "lakehouse-staging"
    S3_CURATED_BUCKET: str = "lakehouse-curated"

    # DuckDB Warehouse Path
    DUCKDB_PATH: Path = Path("./data/warehouse/curated.duckdb")

    # Observability & Alerts
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None

    @property
    def raw_path(self) -> Path:
        """Absolute or relative path to Bronze raw partition root."""
        p = self.LAKEHOUSE_BASE_PATH / "raw"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def staging_path(self) -> Path:
        """Path to Silver staging partition root."""
        p = self.LAKEHOUSE_BASE_PATH / "staging"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def curated_path(self) -> Path:
        """Path to Gold curated partition root."""
        p = self.LAKEHOUSE_BASE_PATH / "curated"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def warehouse_path(self) -> Path:
        """Path to DuckDB warehouse file."""
        self.DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)
        return self.DUCKDB_PATH


settings = Settings()
