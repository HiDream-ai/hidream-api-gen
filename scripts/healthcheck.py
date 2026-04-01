#!/usr/bin/env python3
"""Unified healthcheck for hidream-api-gen.

Checks:
1. token presence
2. dispatcher import/use path
3. optional live probe submission (image/video)
4. requery follow-up for non-terminal tasks

This script is meant to validate the current operational chain:
dispatcher -> submit/poll -> requery -> final status semantics.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.append(PARENT_DIR)

from scripts.common.config import get_token
from scripts.dispatcher import generate
from scripts.requery import poll as requery_poll, build_result_path


def extract_task_id(result: dict[str, Any]) -> str | None:
    return result.get('result', {}).get('task_id')


def detect_module_from_selected_model(selected_model: str) -> tuple[str, str]:
    if selected_model.startswith('kling'):
        return 'video', 'hidream-Q2'
    if selected_model == 'seedance-1.0-pro':
        return 'video', 'hidream-R'
    if selected_model == 'seedance-1.5-pro':
        return 'video', 'hidream-R2-Audio'
    if selected_model.startswith('nano-banana'):
        return 'image', 'hidream-G'
    if selected_model.startswith('seedream'):
        return 'image', 'hidream-M'
    raise ValueError(f'Unknown selected model: {selected_model}')


def main() -> int:
    parser = argparse.ArgumentParser(description='hidream-api-gen healthcheck')
    parser.add_argument('--live', action='store_true', help='Run live submission probes')
    parser.add_argument('--x-source', help='Optional X-source to propagate through the chain')
    parser.add_argument('--timeout', type=int, default=60, help='Requery timeout for live checks')
    args = parser.parse_args()

    report: dict[str, Any] = {
        'token_present': bool(get_token()),
        'live': args.live,
        'checks': [],
    }

    # Static chain check
    try:
        img = generate(
            modality='image',
            prompt='A plain white ceramic cup on a wooden table, neutral studio lighting',
            aspect_ratio='1:1',
            quality_tier='balanced',
            x_source=args.x_source,
        ) if args.live else {'selected_model': 'skipped'}
        report['checks'].append({'name': 'dispatcher_image_path', 'ok': True, 'selected_model': img.get('selected_model')})
    except Exception as e:
        report['checks'].append({'name': 'dispatcher_image_path', 'ok': False, 'error': str(e)})

    try:
        vid = generate(
            modality='video',
            prompt='A white paper airplane slowly gliding across a quiet classroom, gentle daylight, simple motion',
            aspect_ratio='16:9',
            quality_tier='balanced',
            duration=5,
            x_source=args.x_source,
        ) if args.live else {'selected_model': 'skipped'}
        report['checks'].append({'name': 'dispatcher_video_path', 'ok': True, 'selected_model': vid.get('selected_model')})
    except Exception as e:
        report['checks'].append({'name': 'dispatcher_video_path', 'ok': False, 'error': str(e)})

    if args.live:
        for label, obj in [('image_live', img), ('video_live', vid)]:
            if not isinstance(obj, dict) or 'selected_model' not in obj or 'result' not in obj:
                continue
            try:
                selected_model = obj['selected_model']
                task_id = extract_task_id(obj['result'])
                kind, module = detect_module_from_selected_model(selected_model)
                path = build_result_path(kind, module)
                rq = requery_poll(task_id, path, timeout=args.timeout, interval=5, x_source=args.x_source)
                report['checks'].append({
                    'name': f'{label}_requery',
                    'ok': rq.get('terminal') == 'success',
                    'terminal': rq.get('terminal'),
                    'selected_model': selected_model,
                    'task_id': task_id,
                    'statuses': rq.get('statuses'),
                })
            except Exception as e:
                report['checks'].append({'name': f'{label}_requery', 'ok': False, 'error': str(e)})

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
