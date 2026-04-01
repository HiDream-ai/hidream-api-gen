#!/usr/bin/env python3
"""Unified multimodal generation dispatcher for hidream-api-gen.

This module is the single local entry point for image/video generation selection.
It routes by modality + scene constraints, then calls the underlying model runner.
"""
from __future__ import annotations

import uuid
from typing import Any

from scripts.seedream import run as run_seedream
from scripts.kling import run as run_kling
from scripts.common.task_client import parse_images

MODEL_HEALTH: dict[str, dict[str, Any]] = {
    "seedream-M2": {"modality": "image", "status": "degraded", "notes": "submit path works, but current upstream may reject tasks with task_status=2"},
    "seedream-M1": {"modality": "image", "status": "unknown", "notes": "available, lower-res fallback for image generation"},
    "nano-banana-G-std": {"modality": "image", "status": "candidate", "notes": "good fallback candidate for general image generation and edits"},
    "nano-banana-G-pro": {"modality": "image", "status": "candidate", "notes": "higher-tier fallback candidate when quality matters more than speed/cost"},
    "kling-Q2.5T-std": {"modality": "video", "status": "healthy", "notes": "verified for text-to-video and image-to-video"},
    "kling-Q2.5T-pro": {"modality": "video", "status": "candidate", "notes": "higher-tier Kling path when requested"},
    "kling-Q2.6-pro": {"modality": "video", "status": "candidate", "notes": "required for sound=on image-to-video"},
    "seedance-1.0-pro": {"modality": "video", "status": "healthy", "notes": "verified for text-to-video"},
    "seedance-1.5-pro": {"modality": "video", "status": "partial", "notes": "verified for image-to-video; text-only currently rejected upstream"},
}


def health_summary() -> dict[str, dict[str, Any]]:
    return MODEL_HEALTH


def _request_id() -> str:
    return str(uuid.uuid4())


def _normalize_images(images: str | list[str] | None) -> list[str]:
    if isinstance(images, str):
        return parse_images(images)
    return images or []


def _choose_image_model(*, images: str | list[str] | None = None, quality_tier: str = "balanced", preferred_model: str | None = None) -> str:
    if preferred_model:
        return preferred_model
    if images:
        return "nano-banana-G-pro" if quality_tier == "high" else "nano-banana-G-std"
    return "nano-banana-G-pro" if quality_tier == "high" else "nano-banana-G-std"


def _choose_video_model(*, images: str | list[str] | None = None, sound: bool = False, quality_tier: str = "balanced", preferred_model: str | None = None) -> str:
    if preferred_model:
        return preferred_model
    if sound and images:
        return "kling-Q2.6-pro"
    if images:
        return "seedance-1.5-pro" if quality_tier == "high" else "kling-Q2.5T-std"
    return "seedance-1.0-pro" if quality_tier == "high" else "kling-Q2.5T-std"


def generate_image(
    *,
    prompt: str,
    negative_prompt: str | None = None,
    images: str | list[str] | None = None,
    aspect_ratio: str = "1:1",
    resolution: str | None = None,
    quality_tier: str = "balanced",
    preferred_model: str | None = None,
    authorization: str | None = None,
    x_source: str | None = None,
) -> dict[str, Any]:
    model = _choose_image_model(images=images, quality_tier=quality_tier, preferred_model=preferred_model)

    if model.startswith("nano-banana"):
        from scripts.common.base_image import run_task as run_image_task
        version = "G-pro" if model.endswith("G-pro") else "G-std"
        payload = {
            "module": "hidream-G",
            "version": version,
            "request_id": _request_id(),
            "prompt": prompt,
            "images": _normalize_images(images),
            "resolution": resolution or ("2K" if quality_tier == "high" else "1K"),
            "wh_ratio": aspect_ratio,
            "img_count": 1,
        }
        result = run_image_task(payload, authorization, x_source=x_source)
        return {"selected_model": model, "result": result}

    if model.startswith("seedream"):
        version = "M2" if model.endswith("M2") else "M1"
        if resolution is None:
            resolution = "2048*2048" if aspect_ratio == "1:1" else "2048*1152"
        result = run_seedream(
            version=version,
            prompt=prompt,
            negative_prompt=negative_prompt,
            resolution=resolution,
            images=images,
            request_id=_request_id(),
            authorization=authorization,
            x_source=x_source,
        )
        return {"selected_model": model, "result": result}

    raise ValueError(f"Unsupported image model: {model}")


def generate_video(
    *,
    prompt: str,
    negative_prompt: str = "",
    images: str | list[str] | None = None,
    sound: bool = False,
    aspect_ratio: str | None = None,
    duration: int = 5,
    resolution: str | None = None,
    quality_tier: str = "balanced",
    preferred_model: str | None = None,
    authorization: str | None = None,
    x_source: str | None = None,
) -> dict[str, Any]:
    model = _choose_video_model(images=images, sound=sound, quality_tier=quality_tier, preferred_model=preferred_model)

    if model.startswith("kling"):
        version = model.split("kling-", 1)[1]
        result = run_kling(
            version=version,
            prompt=prompt,
            negative_prompt=negative_prompt,
            images=images,
            sound="on" if sound else "off",
            wh_ratio=aspect_ratio or (None if images else "16:9"),
            duration=duration,
            request_id=_request_id(),
            authorization=authorization,
            x_source=x_source,
        )
        return {"selected_model": model, "result": result}

    if model == "seedance-1.0-pro":
        from scripts.common.base_video import run_task as run_video_task
        payload = {
            "module": "hidream-R",
            "version": "R1",
            "request_id": _request_id(),
            "prompt": prompt,
            "images": _normalize_images(images),
            "duration": duration,
            "wh_ratio": aspect_ratio or "adaptive",
            "resolution": resolution or "480p",
            "generate_audio": sound,
        }
        result = run_video_task(payload, authorization, x_source=x_source)
        return {"selected_model": model, "result": result}

    if model == "seedance-1.5-pro":
        from scripts.common.base_video import run_task as run_video_task
        payload = {
            "module": "hidream-R2-Audio",
            "version": "R2-Audio",
            "request_id": _request_id(),
            "prompt": prompt,
            "en_prompt": "",
            "images": _normalize_images(images),
            "duration": duration,
            "wh_ratio": aspect_ratio or ("keep" if images else "16:9"),
            "resolution": resolution or "480p",
            "generate_audio": True if sound else True,
        }
        result = run_video_task(payload, authorization, x_source=x_source)
        return {"selected_model": model, "result": result}

    raise ValueError(f"Unsupported video model: {model}")


def generate(
    *,
    modality: str,
    prompt: str,
    negative_prompt: str | None = None,
    images: str | list[str] | None = None,
    sound: bool = False,
    aspect_ratio: str | None = None,
    duration: int = 5,
    resolution: str | None = None,
    quality_tier: str = "balanced",
    preferred_model: str | None = None,
    authorization: str | None = None,
    x_source: str | None = None,
) -> dict[str, Any]:
    if modality == "image":
        return generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            images=images,
            aspect_ratio=aspect_ratio or "1:1",
            resolution=resolution,
            quality_tier=quality_tier,
            preferred_model=preferred_model,
            authorization=authorization,
            x_source=x_source,
        )
    if modality == "video":
        return generate_video(
            prompt=prompt,
            negative_prompt=negative_prompt or "",
            images=images,
            sound=sound,
            aspect_ratio=aspect_ratio,
            duration=duration,
            resolution=resolution,
            quality_tier=quality_tier,
            preferred_model=preferred_model,
            authorization=authorization,
            x_source=x_source,
        )
    raise ValueError("modality must be 'image' or 'video'")
