"""Configuration management for Aegis AI.

Loads settings from environment variables and .env file.
Supports OpenRouter, Nebius Token Factory, and standard OpenAI-compatible providers.
Enforces security constraints, resource path resolution for builds, and validation.
"""

import os
import sys
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load .env file if present in workspace root
load_dotenv(override=True)


def get_resource_path(relative_path: str) -> Path:
    """Resolve file/directory paths across development, installed wheels, and PyInstaller binaries."""
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller bundled temporary extraction directory
        return Path(sys._MEIPASS) / relative_path

    # Root directory (parent of app/)
    root = Path(__file__).parent.parent.resolve()
    candidate = root / relative_path
    if candidate.exists():
        return candidate

    # Current working directory fallback
    cwd_candidate = Path.cwd() / relative_path
    if cwd_candidate.exists():
        return cwd_candidate

    return candidate


class Settings:
    """Application settings for Aegis AI."""

    def __init__(self) -> None:
        # Unified API key resolution (OpenRouter or Nebius)
        self.api_key: Optional[str] = (
            os.getenv("OPENROUTER_API_KEY", "").strip()
            or os.getenv("NEBIUS_API_KEY", "").strip()
            or os.getenv("LLM_API_KEY", "").strip()
            or None
        )

        # Base URL resolution
        default_base_url = "https://api.tokenfactory.nebius.com/v1/"
        if os.getenv("OPENROUTER_API_KEY") or (self.api_key and "sk-or-" in self.api_key):
            default_base_url = "https://openrouter.ai/api/v1"

        self.base_url: str = (
            os.getenv("OPENROUTER_BASE_URL", "").strip()
            or os.getenv("LLM_BASE_URL", "").strip()
            or os.getenv("NEBIUS_BASE_URL", default_base_url).strip()
        )

        # Model ID resolution
        self.model_id: str = (
            os.getenv("OPENROUTER_MODEL_ID", "").strip()
            or os.getenv("LLM_MODEL_ID", "").strip()
            or os.getenv("NEBIUS_MODEL_ID", "nvidia/nemotron-3-nano-30b-a3b").strip()
        )

        # Workspace path resolution
        raw_workspace = os.getenv("AEGIS_WORKSPACE", "./workspace").strip()
        self.workspace_path: Path = Path(raw_workspace).resolve()

        # Database path resolution
        raw_db = os.getenv("AEGIS_DATABASE_PATH", "./aegis.db").strip()
        self.database_path: Path = Path(raw_db).resolve()

        # Server network binding
        self.host: str = os.getenv("AEGIS_HOST", "127.0.0.1").strip()
        self.port: int = int(os.getenv("AEGIS_PORT", "8000"))
        self.debug: bool = os.getenv("AEGIS_DEBUG", "false").lower() in ("1", "true", "yes")

        # Operational constraints
        self.request_timeout: float = float(os.getenv("AEGIS_REQUEST_TIMEOUT", "30.0"))
        self.max_input_length: int = int(os.getenv("AEGIS_MAX_INPUT_LENGTH", "8000"))
        self.max_output_tokens: int = int(os.getenv("AEGIS_MAX_OUTPUT_TOKENS", "2048"))
        self.max_file_size_bytes: int = int(os.getenv("AEGIS_MAX_FILE_SIZE_BYTES", "1048576"))  # 1 MB

    # Backward compatibility aliases
    @property
    def nebius_api_key(self) -> Optional[str]:
        return self.api_key

    @nebius_api_key.setter
    def nebius_api_key(self, val: Optional[str]) -> None:
        self.api_key = val

    @property
    def nebius_base_url(self) -> str:
        return self.base_url

    @nebius_base_url.setter
    def nebius_base_url(self, val: str) -> None:
        self.base_url = val

    @property
    def nebius_model_id(self) -> str:
        return self.model_id

    @nebius_model_id.setter
    def nebius_model_id(self, val: str) -> None:
        self.model_id = val

    @property
    def is_configured(self) -> bool:
        """Returns True if the required model inference API key is present."""
        return bool(self.api_key and len(self.api_key) > 5)

    def ensure_directories(self) -> None:
        """Ensure necessary local directories exist."""
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
