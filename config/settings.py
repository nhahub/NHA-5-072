import os
from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "Atlas AQAR"
    VERSION: str = "0.1.0"
    ENVIRONMENT: Literal["development", "testing", "production"] = "development"
    LOG_LEVEL: str = "INFO"

    # Base Paths
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    RAW_DATA_DIR: Path = BASE_DIR / "data" / "raw"
    PROCESSED_DATA_DIR: Path = BASE_DIR / "data" / "processed"
    CHROMA_PERSIST_DIRECTORY: str = str(BASE_DIR / "data" / "chroma_db")
    BENCHMARKS_DIR: Path = BASE_DIR / "data" / "benchmarks"

    # API Keys
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    TAVILY_API_KEY: str | None = None
    SERPAPI_API_KEY: str | None = None

    # LLM Settings
    LLM_PROVIDER: Literal["openai", "anthropic", "gemini", "offline"] = "offline"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.1

    # Chroma
    CHROMA_COLLECTION_NAME: str = "atlas_aqar_knowledge"

    # Autonomy & Bounded Guardrails
    MAX_GRAPH_ITERATIONS: int = 10
    MAX_CRITIC_RETRIES: int = 3
    MAX_REACT_STEPS: int = 8
    TOKEN_BUDGET: int = 100_000
    TIMEOUT_SECONDS: int = 180

    # API Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
