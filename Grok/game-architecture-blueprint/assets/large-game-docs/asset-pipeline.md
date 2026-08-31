# Asset Pipeline

Art direction lives in the GDD (`06-art-audio-juice.md`). This file is import, naming, and ownership.

## Import Contract
Resolution, pixels-per-unit / scale, filter (nearest vs bilinear), atlas vs discrete, keyable background color, animation fps.

## Naming And Layout
Directory tree under `assets/` with purpose per folder.

## Style Lock
Path to the lock image (or "greybox-only this milestone"). All character/tile/UI sets depend on it.

## Specialist Routing
Use kinds the orchestrator understands: `style-lock`, `sprite`, `character`, `animation`, `tileset`, `ui`, `vfx`, `icon`. Specialist skills: `game-asset-core` plus `game-character-consistency` / `game-animation-frames` / `game-tilesets` / `game-ui-icons`.

The machine-readable list lives in `implementation-plan.md` under `assets:`. Keep this file as the human explanation; do not duplicate every row here.

## Audio
What can be generated vs stubbed. If no viable generator, list stubs and the gap — do not pretend SFX exist.
