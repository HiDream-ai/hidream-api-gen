#!/usr/bin/env python3
"""OpenClaw API Configuration Helper."""
from __future__ import annotations

import os
import sys

# Ensure we can import from common
sys.path.insert(0, os.path.dirname(__file__))

from common.config import get_token, set_token


def main():
    print("\nHiDream API Gen Configuration")
    print("-----------------------------")
    
    current = get_token()
    masked = "***"
    if current:
        if len(current) > 8:
            masked = current[:4] + "..." + current[-4:]
        else:
            masked = current
        print(f"Current token: {masked}")
    else:
        print("Current token: Not set")
    
    print("\nPlease enter your HIDREAM_AUTHORIZATION token (from vivago.ai/platform/token).")
    print("Leave empty to keep current configuration.")
    token = input("Token: ").strip()
    
    if not token:
        if current:
            print("No changes made.")
        else:
            print("No token provided. Exiting.")
        return

    try:
        set_token(token)
        print(f"Token saved to ~/.config/openclaw/hidream_config.json")
    except Exception as e:
        print(f"Error saving token: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
