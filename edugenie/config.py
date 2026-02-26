"""Configuration helpers for environment-driven settings."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    openrouter_api_key: str
    openrouter_model: str = "openrouter/free"


def get_settings() -> Settings:
    """Build validated settings for app runtime."""
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    model = os.getenv("OPENROUTER_MODEL", "openrouter/free").strip()
    return Settings(openrouter_api_key=api_key, openrouter_model=model)
