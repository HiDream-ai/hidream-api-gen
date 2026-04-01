# hidream-api-gen status board

A very short operational index for what is currently active, degraded, or removed.

## Active

| Model / Surface | Status | Last verified | Notes |
|---|---|---|---|
| Kling | active | 2026-03-24 | live healthcheck succeeded |
| Seedance 1.0 Pro | active | 2026-03-24 | verified in prior runtime checks |
| Seedance 1.5 Pro | active | 2026-03-24 | verified for image-to-video; text-only not safe default |
| Seedream | active | 2026-03-24 | image path available |
| Nano Banana | active | 2026-03-24 | live healthcheck image path succeeded |
| Dispatcher chain | active | 2026-03-24 | dispatcher → requery → success verified |
| Healthcheck | active | 2026-03-24 | static and live checks landed |

## Degraded

| Model / Surface | Status | Last verified | Notes |
|---|---|---|---|
| Sora 2 Pro | degraded | 2026-03-24 | currently observed at `task_status=3` |

## Removed

| Model / Surface | Status | Last verified | Notes |
|---|---|---|---|
| Hailuo 02 | removed | 2026-03-24 | removed from active surface; current vivago runtime returns `code=2031` |

## Not fully wrapped yet

| Family | Status | Last verified | Notes |
|---|---|---|---|
| text | partial | 2026-03-24 | API family recognized; full generation wrappers not landed |
| audio | partial | 2026-03-24 | API family recognized; full generation wrappers not landed |
