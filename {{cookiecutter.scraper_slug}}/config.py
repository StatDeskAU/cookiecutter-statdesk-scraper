"""Pydantic v2 config for {{ cookiecutter.scraper_slug }}.

Loads from env + optional `.env` file (python-dotenv).
"""
from __future__ import annotations

import base64
import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


def _decode_b64_password(plain_key: str, b64_key: str) -> str:
    """Return env[plain_key] if set, else base64-decode env[b64_key]."""
    plain = os.environ.get(plain_key, "")
    if plain:
        return plain
    b64 = os.environ.get(b64_key, "")
    if b64:
        try:
            return base64.b64decode(b64).decode("utf-8")
        except (ValueError, UnicodeDecodeError) as exc:
            raise RuntimeError(
                f"{b64_key} is set but cannot be base64-decoded. "
                "Re-encode with: echo -n '<password>' | base64"
            ) from exc
    return ""


class DatabaseConfig(BaseModel):
    """scraper-portfolio-pg connection details (libpq-standard names)."""

    host: str = Field(default_factory=lambda: os.environ.get("PGHOST", "localhost"))
    port: int = Field(default_factory=lambda: int(os.environ.get("PGPORT", "5432")))
    user: str = Field(default_factory=lambda: os.environ.get("PGUSER", "postgres"))
    password: str = Field(default_factory=lambda: os.environ.get("PGPASSWORD", ""))
    database: str = Field(default_factory=lambda: os.environ.get("PGDATABASE", "{{ cookiecutter.pg_database }}"))


class SupabaseConfig(BaseModel):
    """Supabase pooler connection details. Only used by the warehouse mirror."""

    host: str = Field(default_factory=lambda: os.environ.get("SUPABASE_PG_HOST", ""))
    port: int = Field(default_factory=lambda: int(os.environ.get("SUPABASE_PG_PORT", "6543")))
    user: str = Field(default_factory=lambda: os.environ.get("SUPABASE_PG_USER", ""))
    database: str = Field(default_factory=lambda: os.environ.get("SUPABASE_PG_DATABASE", "postgres"))
    password: str = Field(
        default_factory=lambda: _decode_b64_password("SUPABASE_PG_PASSWORD", "SUPABASE_PG_PASSWORD_B64")
    )

    def is_configured(self) -> bool:
        return bool(self.host and self.user and self.password)


class AppConfig(BaseModel):
    """Top-level config for {{ cookiecutter.scraper_slug }}."""

    db: DatabaseConfig = Field(default_factory=DatabaseConfig)
    supabase: SupabaseConfig = Field(default_factory=SupabaseConfig)


def load_config() -> AppConfig:
    return AppConfig()
