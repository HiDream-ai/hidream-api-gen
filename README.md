# HiDream API Gen Skills

A local HiDream/Vivago image + video generation package for this workspace.

Runtime host: `vivago.ai`

## What this package is for

In this workspace, `hidream-api-gen` is the **default multimodal generation gateway** for local API-backed image/video generation.

That includes not only ordinary image/video requests, but also cases where a higher-level workflow has already narrowed down to actual multimodal asset generation, such as:
- one story video / OSV asset-generation steps
- comic / manga / 漫画生成 flows
- local `comic-gen`-style workflows once they reach the actual image/video generation step

Important boundary:
- higher-level project/workflow routing should still be handled by the appropriate domain/router skill
- but once the task is specifically “generate the asset through the local multimodal API path”, this package is the preferred gateway

## Canonical entrypoints

Use these entrypoints in order of role:
- `scripts/dispatcher.py` → canonical generation entry
- `scripts/requery.py` → explicit follow-up for an existing `task_id`
- `scripts/healthcheck.py` → chain validation / smoke test

Treat raw per-model scripts as implementation backends.
Do not build new default workflows around calling them directly.

## Current scope

### Active
- image generation
- video generation
- re-query / polling discipline
- healthcheck / smoke-test path

### Recognized but not fully wrapped
- text family
- audio family

`requery.py` can poll `text` / `audio` kinds, but full generation wrappers + dispatcher integration for those families are not yet landed.

## Current support surface

### Supported / active
- **Kling**
- **Seedance 1.0 Pro**
- **Seedance 1.5 Pro**
- **Seedream**
- **Nano Banana**

### Removed from active surface
- **Sora 2 Pro**
- **Hailuo 02**

For current alignment details, see:
- `references/model-mapping.md`
- `references/status-board.md`
- `references/verification-log.md`

## Status semantics

Current operative contract:
- `0` = queued
- `1` = success
- `2` = in progress / non-terminal
- `3` = generation failed
- `4` = safety review failed

Hard rule:
- if a task is at `task_status=2`, do **not** classify it as failure
- continue polling or use `scripts/requery.py`

## Runtime requirements

- `HIDREAM_AUTHORIZATION` → required
- `HIDREAM_ENDPOINT` → optional override
- `X-source` → optional upstream routing/review marker

## Quick start

### Healthcheck

```bash
python3 scripts/healthcheck.py
python3 scripts/healthcheck.py --live
```

### Re-query an existing task

```bash
python3 scripts/requery.py --task-id <TASK_ID> --kind video --module hidream-Q2
```

### Example backend CLI usage

```bash
python3 scripts/kling.py --version "Q2.5T-std" --prompt "A flying car"
```

## Where the details live

- runtime gateway guidance → `SKILL.md`
- model alignment → `references/model-mapping.md`
- canonical entry → `scripts/dispatcher.py`
- explicit follow-up → `scripts/requery.py`
- chain validation → `scripts/healthcheck.py`

## Security notes

- reads `HIDREAM_AUTHORIZATION` from env/config
- reads user-provided local media files for upload/base64 conversion when needed
- sends requests only to the configured Vivago endpoint
