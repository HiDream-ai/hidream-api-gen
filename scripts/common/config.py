from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from pathlib import Path

# Unified config directory (XDG Base Directory compliant)
CONFIG_DIR = Path.home() / ".config" / "openclaw"
CONFIG_FILE = CONFIG_DIR / "hidream_config.json"


def _ensure_config_dir() -> None:
    """Ensure the config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def _exchange_ticket_for_token(ticket: str) -> str | None:
    """Exchange ticket for API token via Vivago API."""
    url = "https://vivago.ai/prod-api/user/v3/api-key/transform"
    try:
        req = urllib.request.Request(url, headers={"Cookie": f"ticket={ticket}"})
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                if data.get("code") == 0 and "result" in data:
                    return data["result"].get("token")
    except Exception:
        pass
    return None


def get_token() -> str | None:
    """
    Get authorization token from environment variables or config file.
    Priority:
    1. HIDREAM_AUTHORIZATION env var
    2. OPENCLAW_AUTHORIZATION env var (legacy)
    3. ~/openclaw/.env (HIDREAM_AUTHORIZATION or ticket exchange)
    4. ~/.config/openclaw/hidream_config.json (unified config)
    """
    # 1. Check Env
    token = os.getenv("HIDREAM_AUTHORIZATION") or os.getenv("OPENCLAW_AUTHORIZATION")
    if token:
        return token

    # 2. Check ~/openclaw/.env (Fallback)
    openclaw_env = Path.home() / "openclaw" / ".env"
    if openclaw_env.exists():
        found_ticket = None
        try:
            with open(openclaw_env, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("HIDREAM_AUTHORIZATION="):
                        parts = line.split("=", 1)
                        if len(parts) == 2:
                            val = parts[1].strip().strip("'").strip('"')
                            if val:
                                return val
                    elif line.startswith("ticket="):
                        parts = line.split("=", 1)
                        if len(parts) == 2:
                            val = parts[1].strip().strip("'").strip('"')
                            if val:
                                found_ticket = val
            
            # If we found a ticket but no direct authorization, try to exchange it
            if found_ticket:
                exchanged_token = _exchange_ticket_for_token(found_ticket)
                if exchanged_token:
                    return exchanged_token
        except Exception:
            pass

    # 3. Check Config File
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                return data.get("authorization")
        except Exception:
            pass
    return None


def set_token(token: str) -> None:
    """Save authorization token to unified config file."""
    _ensure_config_dir()
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
