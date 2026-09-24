# Asset Production

How an `[asset-artist]` produces and verifies game art in Claude Code. Claude has no built-in image generator, but it can write SVG, write scripts that draw pixels, write runtime drawing code, and — crucially — **look at the result** (the Read tool renders PNG/JPG). The whole method rests on that loop: produce → render → look → compare to spec → fix.

Contents: Choosing by method · Style lock · code-vector · code-raster · procedural · image-gen · greybox · external · Verification (all methods) · Audio · Legacy manifests

## Choosing by method

The Asset Manifest row's `method` decides the path. Don't switch methods on your own; if a method can't reach the spec, report it to the lead with a proposed alternative.

| method | Output | Owned files |
|---|---|---|
| `code-vector` | `.svg` (and rasterized `.png` if the engine needs bitmaps) | the SVGs, the PNGs, any rasterize script |
| `code-raster` | `.png` sprites / sheets / tiles | generator script (e.g. `tools/art/player.py`) **and** its outputs |
| `procedural` | runtime code (e.g. `src/fx/sparks.ts`) | the code module |
| `image-gen` | `.png` from an image-generation tool | the outputs + a prompt log |
| `greybox` | flat placeholder shapes | outputs (or runtime code) |
| `external` | user-supplied files | only wiring/import notes |

## Style lock

The style lock is produced first, by one artist, and every later visual asset depends on it. It has three parts:

1. **Palette** — `assets/style/palette.json`: a small named set of hex colors (e.g. 8–24 for pixel art), with roles (outline, shadow, highlight, UI accent, danger). Palette discipline is what makes code-drawn art look intentional rather than programmer-art.
2. **Rules note** — `assets/style/style-rules.md`: canvas/tile size, pixels-per-unit, outline weight and color, light direction, shading style (flat / 2-tone / dithered), proportions (e.g. "characters 2.5 heads tall"), corner radius, stroke caps, how readable silhouettes must be at game scale.
3. **Reference sheet** — `assets/style/style-lock.png`: one sample of each asset family (a character, a tile, a UI button, an icon, a VFX frame) drawn by the rules, side by side on the game's background color.

Derive all three from GDD `06-art-audio-juice.md` and the architecture's import contract. View the sheet at game scale before declaring it done. Later artists **read** the lock; they never edit it.

## code-vector

Write SVG by hand as text. It suits flat, geometric, clean-lined, UI, and icon styles.

- Set `viewBox` to the asset's logical size; use only palette colors (reference them from `palette.json` — copy exact hex values).
- Build shapes from simple primitives and paths; group by part (`<g id="arm-left">`) so animation or variants can reuse them.
- Keep silhouettes bold. Detail that disappears at game scale is wasted.
- For variants (enemy colors, button states), write one base SVG and generate the others by a small script substituting palette entries, so they can't drift.
- **Rasterizing** when the engine wants PNGs: use whatever is available — `rsvg-convert -w W -h H in.svg -o out.png`, Python `cairosvg`, Node `sharp`, or a Playwright/Chromium screenshot of the SVG. Check availability first (`which rsvg-convert`, `python3 -c "import cairosvg"`); don't install system packages without the lead's OK. Commit the rasterize command to the owned script so it's reproducible.
- Web engines can load SVG directly; keep it as SVG unless the import contract says otherwise.

## code-raster

Write a deterministic script that draws the pixels — typically Python + Pillow (`python3 -c "import PIL"` to check), or Node canvas if that's what the project has.

- One generator script per asset family under the owned tools path (e.g. `tools/art/tiles.py`). Re-running it must reproduce the output byte-for-byte: no unseeded randomness (use `random.Random(seed)`).
- Load colors from `palette.json`; never hard-code off-palette colors.
- **Pixel art:** draw at native resolution (e.g. 16×16, 32×32) on a transparent RGBA canvas, one pixel at a time or via small helpers (`rect`, `line`, `outline(mask)`, `shade(mask, light_dir)`). Describe the sprite as a grid or layered masks in the script so it's editable. Preview upscaled with `Image.NEAREST` — never bilinear.
- **Sprite sheets / animation:** fixed cell size, frames in a row per animation, consistent anchor point (feet at the same pixel row). Build frames from a shared base pose plus per-frame deltas so the character stays on-model. Emit a small JSON/atlas descriptor if the import contract asks for one.
- **Tiles:** match edges — generate autotile variants from shared edge definitions and test by composing a small map preview with the tiles placed next to each other.
- **Painterly-ish effects** are possible within limits (gradients, noise with a seeded generator, dithering), but don't promise illustration quality; flag if the GDD asks for it.

## procedural

Art drawn at runtime by game code — particles, trails, screen flashes, simple geometric actors, animated UI. It's code, so it lives in an owned module and follows the implementer rules as well (don't touch systems you don't own). Expose tunables (colors from the palette, counts, lifetimes) as data. Verify via the screenshot command, capturing the moment the effect is on screen.

## image-gen

Only when the session actually has an image-generation tool (an MCP server or API the user configured). If you can't find one, stop and report — don't substitute silently.

- Build prompts from the style rules + the manifest row (subject, pose, framing, background, size). Keep a prompt log next to the outputs (`assets/.../prompts.md`) so results can be regenerated.
- If the tool accepts a reference image, pass the style lock (edit-chaining from the lock keeps sets consistent). Never regenerate a character from scratch when a lock or base image exists.
- Post-process with a script: crop, resize to the import size, remove the background to transparency, snap to palette if the style is pixel/limited-palette.
- Generated art drifts; verification (below) is not optional.

## greybox

Flat, clearly labeled placeholders: one consistent color per entity type, correct size and anchor, a text label or simple glyph. The point is correct *dimensions and alignment*, so the real art drops in without breaking layout. Greybox is a legitimate deliverable when the manifest says so — label it as greybox in your report.

## external

The user or a human artist supplies files. Verify they exist at the manifest path, check dimensions/format/transparency against the import contract, note license/source if given, and report mismatches. Don't edit them unless asked.

## Verification (all methods)

Do this for every asset before reporting done:

1. **Render** to PNG if it isn't one already.
2. **Run the QA script**: `python3 <game-dev-orchestrator skill dir>/scripts/asset_qa.py <images...> --palette assets/style/palette.json --sheet tmp/asset-qa/<name>-sheet.png --scale 4` — reports size, alpha, color count, off-palette pixels, opaque bounding box, and writes a nearest-neighbor contact sheet on the game background. (If Pillow is missing, do the equivalent checks manually and say so.)
3. **Look** at the contact sheet with the Read tool. Write a **blind description** first — what you actually see, before re-reading the spec — then compare it to the manifest row and the style lock. Seeing what you *meant* to draw instead of what's there is the classic failure; the blind description guards against it.
4. **Check at game scale**: is the silhouette readable at 1× on the game background? Are frames aligned (no jitter in the anchor)? Do tiles seam?
5. Fix and repeat. After at most 3 rounds, stop and report remaining defects honestly rather than looping.

Report per asset: path, method, dimensions, pass/fail against each spec item, remaining defects, and which lock/base image you worked from.

## Audio

- `procedural`: synthesize short SFX with a script (Python stdlib `wave` + `math`, or numpy if present): square/triangle/noise oscillators, pitch sweeps, ADSR envelopes — jsfxr-style blips, jumps, hits, pickups. For web games, WebAudio synthesis at runtime is also fine. Keep generator scripts owned and deterministic.
- `external`: wire supplied files.
- `stub`: short silent files with the right names and a gap entry in the progress file.
- Music is out of reach for code synthesis beyond simple loops; stub it and flag it unless the manifest says otherwise.
- You can't listen to audio. Verify format, duration, peak level (no clipping), and naming; mark "sounds right" as `needs-human`.

## Legacy manifests

Manifests written by the Grok version of this pipeline have `skill: game-asset-core` (+ a specialist) instead of `method`. Map them, record the mapping in the progress file, and confirm with the user if art quality expectations change:

| Legacy kind / specialist | Suggested method |
|---|---|
| `style-lock` | same style as the GDD: `code-raster` for pixel art, `code-vector` for flat/vector |
| `sprite`, `character` (+ `game-character-consistency`) | `code-raster` (pixel) or `code-vector` (flat) |
| `animation` (+ `game-animation-frames`) | `code-raster` sprite sheet |
| `tileset` (+ `game-tilesets`) | `code-raster` |
| `ui`, `icon` (+ `game-ui-icons`) | `code-vector` |
| `vfx` | `procedural` |
| painterly / illustrated / photoreal anything | `image-gen` if a tool exists, otherwise `greybox` + flag |
