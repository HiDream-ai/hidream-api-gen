from __future__ import annotations

import json
import os
from pathlib import Path

# Project root (hidream-api-gen/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_FILE = PROJECT_ROOT / ".hidream_config.json"


def get_token() -> str | None:
    """
    Get authorization token from environment variables or config file.
    Priority:
    1. HIDREAM_AUTHORIZATION env var
    2. OPENCLAW_AUTHORIZATION env var (legacy)
    3. .hidream_config.json (in project root)
    """
    # 1. Check Env
    token = os.getenv("HIDREAM_AUTHORIZATION") or os.getenv("OPENCLAW_AUTHORIZATION")
    if token:
        return token

    # 2. Check Config File
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                return data.get("authorization")
        except Exception:
            pass
    return None


def set_token(token: str) -> None:
    """Save authorization token to config file."""
    data = {}
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
        except Exception:
            pass

    data["authorization"] = token
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)
