"""Configuration management for the travel planner."""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # LLM Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    ollama_temperature: float = 0.3

    # Embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    # Vector Store
    vector_store_type: str = "faiss"
    vector_store_path: Path = Path("./data/vector_stores")

    # Data Paths
    data_raw_path: Path = Path("./data/raw")
    data_processed_path: Path = Path("./data/processed")

    # Retrieval Settings
    max_retrieval_results: int = 10
    chunk_size: int = 500
    chunk_overlap: int = 50

    # Planning Constraints
    default_daily_budget: float = 50.0
    default_walking_speed_kmh: float = 4.0
    max_daily_walking_km: float = 10.0
    max_attraction_distance_km: float = 2.0

    # Logging
    log_level: str = "INFO"
    log_file: Optional[Path] = Path("./logs/app.log")

    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        directories = [
            self.vector_store_path,
            self.data_raw_path,
            self.data_processed_path,
        ]
        
        if self.log_file:
            directories.append(self.log_file.parent)
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.ensure_directories()