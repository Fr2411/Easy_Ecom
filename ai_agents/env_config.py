"""Environment helpers for AI agent runtime configuration."""

from __future__ import annotations

import os
from pathlib import Path


def _read_env_file_value(env_path: Path, key: str) -> str | None:
    if not env_path.exists() or not env_path.is_file():
        return None

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        current_key, value = line.split("=", 1)
        if current_key.strip() != key:
            continue
        return value.strip().strip('"').strip("'")

    return None


def get_config_value(key: str, default: str = "") -> str:
    """Resolve env config from process env, `.env`, then `.env.example`."""
    process_value = os.getenv(key)
    if process_value:
        return process_value

    for filename in (".env", ".env.example"):
        file_value = _read_env_file_value(Path(filename), key)
        if file_value:
            return file_value

    return default
