---
name: hidream-aigc-skills
description: |
  Gateway skill for local HiDream/Vivago image and video generation on vivago.ai.
  Use when the user wants to generate images or videos through the local API-backed path.
---

# HiDream AIGC Gateway

This is the **gateway skill** for local HiDream / Vivago image and video generation.
It should act as the first routing layer for requests that clearly belong to this generation stack.

## Core role

This skill exists to answer:
1. is the request really for HiDream/Vivago-backed generation?
2. is the user asking for image generation, video generation, or a related media-generation path?
3. what downstream generation or recovery path should own execution?

It is a gateway, not the final per-model executor.

## Use this skill when

The user clearly wants:
- local API-backed image generation
- local API-backed video generation
- text-to-image / text-to-video / image-to-video in the HiDream/Vivago path
- comic / manga / asset-generation requests that should route into this local generation family

## Routing posture

Treat this skill as the family entry, not the whole workflow.
Its job is to:
- confirm the generation family
- identify the media type and rough path
- choose the right downstream execution or requery path
- keep generation requests from being prematurely absorbed by unrelated project routers

## Success condition

Success means:
- the request is correctly identified as belonging to the HiDream/Vivago generation family
- the right downstream path is chosen
- generation execution receives a clearer media/object path than the original user wording provided

## Boundaries

This skill should not act like every image/video request belongs here by default.
It should not absorb broader comic / OSV / project-level planning when the user is still deciding the real object path.
It should not replace downstream execution-specific handling.

## Default model preference

For requests in this HiDream/Vivago family that do not include an explicit model choice, use these defaults:
- text-to-image → `nano-banana-G-std`
- text-to-video → `seedance`
- image-to-video → `seedance`

Treat these as user-preference defaults, not hard overrides:
- if the user names another model, follow the user
- if a downstream executor has a stricter compatibility requirement for a specific path, surface that constraint and adapt
- do not add a follow-up question just to choose among available models when no special reason exists

## Main anti-patterns

- routing every media request into HiDream just because generation is mentioned
- confusing project-level planning with generation-family routing
- skipping object/media-type clarification and forcing execution too early
- letting downstream model specifics bloat the gateway file
