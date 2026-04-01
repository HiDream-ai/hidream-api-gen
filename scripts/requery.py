#!/usr/bin/env python3
"""Re-query and poll existing HiDream tasks until terminal success/failure/timeout.

Usage examples:
  python3 scripts/requery.py --task-id <id> --path /api-pub/gw/v4/video/hidream-Q2/async/results
  python3 scripts/requery.py --task-id <id> --kind image --module hidream-G
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any

import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.append(PARENT_DIR)

from scripts.common.config import get_token

ENDPOINT = os.getenv("HIDREAM_ENDPOINT") or os.getenv("OPENCLAW_ENDPOINT", "https://vivago.ai")
DEFAULT_POLL_INTERVAL = 5
DEFAULT_TIMEOUT = 300


def build_result_path(kind: str, module: str) -> str:
    return f"/api-pub/gw/v4/{kind}/{module}/async/results"


def headers(token: str, x_source: str | None = None) -> dict[str, str]:
    head = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    if x_source:
        head["X-source"] = x_source
    return head


def poll(task_id: str, path: str, timeout: int = DEFAULT_TIMEOUT, interval: int = DEFAULT_POLL_INTERVAL, x_source: str | None = None) -> dict[str, Any]:
    token = get_token()
    if not token:
        raise ValueError("Missing authorization. Run 'scripts/configure.py' or set HIDREAM_AUTHORIZATION.")
    url = ENDPOINT + path
    start = time.time()
    last_json: dict[str, Any] | None = None

    while True:
        resp = requests.get(url, params={"task_id": task_id}, headers=headers(token, x_source=x_source), timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(f"http error: {resp.status_code} {resp.text}")
        data = resp.json()
        if data.get("code") != 0:
            raise RuntimeError(f"query failed: {json.dumps(data, ensure_ascii=False)}")

        last_json = data
        sub_tasks = data.get("result", {}).get("sub_task_results", []) or []
        statuses = [st.get("task_status") for st in sub_tasks]
        has_media = any(any(k in st for k in ("video", "image", "url", "media", "output", "audio")) for st in sub_tasks)

        if sub_tasks and all(status == 1 for status in statuses) and has_media:
            return {
                "terminal": "success",
                "task_id": task_id,
                "path": path,
                "statuses": statuses,
                "result": data,
            }

        if any(status in {3, 4} for status in statuses):
            return {
                "terminal": "failure",
                "task_id": task_id,
                "path": path,
                "statuses": statuses,
                "result": data,
            }

        known_transient = {-5, -4, -3, -2, -1, 0, 2}
        if statuses and all(status not in known_transient and status != 1 for status in statuses):
            return {
                "terminal": "unknown",
                "task_id": task_id,
                "path": path,
                "statuses": statuses,
                "result": data,
            }

        if time.time() - start >= timeout:
            return {
                "terminal": "timeout",
                "task_id": task_id,
                "path": path,
                "statuses": statuses,
                "result": last_json,
            }

        time.sleep(interval)


def main() -> int:
    parser = argparse.ArgumentParser(description="Re-query HiDream task result until terminal state")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--path", help="Explicit /results path")
    parser.add_argument("--kind", choices=["image", "video", "text", "audio"], help="resource kind; used with --module")
    parser.add_argument("--module", help="module name, e.g. hidream-G / hidream-Q2 / hidream-R")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--interval", type=int, default=DEFAULT_POLL_INTERVAL)
    parser.add_argument("--x-source", help="Optional task source marker for upstream routing/review strategy.")
    args = parser.parse_args()

    path = args.path
    if not path:
        if not args.kind or not args.module:
            raise SystemExit("Either --path or both --kind and --module are required")
        path = build_result_path(args.kind, args.module)

    try:
        result = poll(args.task_id, path, timeout=args.timeout, interval=args.interval, x_source=args.x_source)
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False))
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
