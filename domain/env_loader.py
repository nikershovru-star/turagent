"""PHASE 0: Security — .env и конфигурация."""
from __future__ import annotations

import os
from pathlib import Path


def load_env(env_path: Path | str | None = None) -> None:
    """Загружает .env в os.environ."""
    if env_path is None:
        env_path = Path(__file__).resolve().parent.parent / ".env"
    env_path = Path(env_path)
    if not env_path.exists():
        return
    with env_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip().strip('"').strip("'")


# .env already loaded by app before domain.config import
# или вызови load_env() явно в main.py до импорта domain.config
