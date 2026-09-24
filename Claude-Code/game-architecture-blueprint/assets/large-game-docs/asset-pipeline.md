# Asset Pipeline

Art direction lives in the GDD (`06-art-audio-juice.md`). This file is production method, import, naming, and ownership.

## Production Methods
Which `method` each asset family uses and why it fits the GDD art direction:

| Asset family | kind | method | Why |
|---|---|---|---|
| | style-lock | | |
| | sprite / character / animation / tileset / ui / icon / vfx | code-vector / code-raster / procedural / image-gen / greybox / external | |

`image-gen` only if the user confirmed a generation tool (MCP server or API) exists in their Claude Code setup; otherwise name the code-drawn or greybox fallback. If the GDD's style can't be reached with the available methods, say so here and record it as a risk.

## Import Contract
Resolution, pixels-per-unit / scale, filter (nearest vs bilinear), atlas vs discrete, transparency/background, animation fps, SVG vs rasterized-at-build.

## Naming And Layout
Directory tree under `assets/` with purpose per folder. Where generator scripts live (e.g. `tools/art/*.py`) — those scripts are owned files too, and re-running them must reproduce the asset.

## Style Lock
Path to the lock files (or "greybox-only this milestone"):
- palette (hex values, e.g. `assets/style/palette.json`)
- reference sheet image showing proportions, outline weight, shading, one sample of each asset family
- short rules note (`assets/style/style-rules.md`)

All character/tile/UI sets depend on it so parallel artists stay consistent.

## Kinds
Use kinds the orchestrator understands: `style-lock`, `sprite`, `character`, `animation`, `tileset`, `ui`, `vfx`, `icon`, `audio`.

The machine-readable list lives in `implementation-plan.md` under `assets:`. Keep this file as the human explanation; don't duplicate every row here.

## Audio
Per sound family: `procedural` (synthesized SFX, WebAudio tones), `external`, or `stub`. List stubs and the gap — never pretend SFX exist.
