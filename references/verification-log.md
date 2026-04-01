# hidream-api-gen verification log

A short time-ordered record of important runtime and governance verification events.

## 2026-03-24

- Re-established `hidream-api-gen` as the local multimodal generation gateway.
- Added canonical runtime chain:
  - `scripts/dispatcher.py`
  - `scripts/requery.py`
  - `scripts/healthcheck.py`
- Corrected task-status handling:
  - `1` = success
  - `2` = non-terminal / continue polling
- Verified by direct re-query that tasks seen at `task_status=2` can later settle at `task_status=1` with final media.
- Added live healthcheck and confirmed the chain:
  - dispatcher → submit/poll → requery → success
- Confirmed runtime host should remain `vivago.ai` for the current token, while domestic documentation may still be used as protocol reference.
- Added optional `X-source` support through the active generation chain.
- Removed Hailuo 02 from the active support surface after live validation in current `vivago.ai` environment returned `code=2031`.
- Rebuilt `SKILL.md` as a gateway-skill runtime cognition layer.
- Slimmed `README.md` into a human-facing entry page.
- Added maintenance indexes:
  - `references/model-mapping.md`
  - `references/status-board.md`

## How to use this file

Use this as the shortest time-line answer to:
- what was verified recently
- what was removed recently
- what runtime assumptions are currently active

Do not turn this into a noisy diary.
Only append major verification, removal, or support-surface changes.
