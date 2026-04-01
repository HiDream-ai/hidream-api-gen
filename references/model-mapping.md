# hidream-api-gen model mapping

This file aligns local script entrypoints with current runtime module/version pairs and the nearest official parameter families referenced from internal API notes.

## Scope boundary

Current local implementation focus:
- **Implemented / operational focus**: image + video
- **Recognized but not fully wrapped yet**: text + audio

That means this skill should currently be presented as a practical image/video client first, not as a fully wrapped all-family SDK.

---

## Video

| Local script | Module | Version | Intended task shape | Nearest official params family | Current status |
|---|---|---:|---|---|---|
| `scripts/kling.py` | `hidream-Q2` | `Q2.5T-std` / `Q2.5T-pro` / `Q2.6-pro` | text-to-video / image-to-video | `ApiVolceJmTxt2vidV30pParams` and related Volce JM video families | Verified for T2V and I2V |
| `scripts/seedance_1_0_pro.py` | `hidream-R` | `R1` | text-to-video | `ApiVolceJmTxt2vidV30pParams` (nearest known family) | Verified for T2V |
| `scripts/seedance_1_5_pro.py` | `hidream-R2-Audio` | `R2-Audio` | image-to-video | `ApiVolceJmImg2vid...` family (nearest known family) | Verified for I2V; text-only not safe default |
| `scripts/sora_2_pro.py` | `sora` | `sora-2-p` | video generation | no confirmed official family name from current note | Disabled from active routing; standalone diagnostic only. Current upstream tasks observed at status 3 |

## Image

| Local script | Module | Version | Intended task shape | Nearest official params family | Current status |
|---|---|---:|---|---|---|
| `scripts/seedream.py` | `hidream-M` | `M1` / `M2` | text-to-image / image-conditioned generation | `ApiVolceJmTxt2imgV40Params` (nearest known family) | Verified in prior tests |
| `scripts/nano_banana.py` | `hidream-G` | `G-std` / `G-pro` | image generation / edit-style flow | `ApiNanoBananaParams` | Verified in prior tests |

## Text / Audio families

Internal notes indicate these API families exist:
- text: `/api-pub/gw/v4/text/<module>/async`
- audio: `/api-pub/gw/v4/audio/<module>/async`

Nearest referenced official params families from current notes:
- text: `ApiVolceAudio2TxtParams`
- audio: `ApiMinimaxSpeechParams`

Current local state:
- family shape recognized
- `requery.py` already accepts `--kind text|audio`
- **full generation wrappers / dispatcher integration are not yet implemented**

## Operational notes

- Runtime endpoint remains `vivago.ai` for current token usage.
- Internal domestic-site documentation is still useful as protocol reference.
- `task_status=2` must be treated as non-terminal/in-progress and re-queried.
- `task_status=1` is terminal success.
- `task_status=3` = generation failed.
- `task_status=4` = safety review failed.
