---
name: create-brandkit
description: >
  Generate, modify, and iterate on logos, icons, favicons, banners, and other
  brand/visual assets using the BrandKit image-generation API. Use this skill
  whenever the user asks you to create, generate, design, edit, or refine a
  logo, app icon, favicon, banner, hero image, brand asset, or any visual
  graphic for their project. Also trigger when the user mentions "brandkit",
  "brand kit", or asks for image generation for branding purposes. Even if the
  user just says "add a logo" or "I need an icon for my app", use this skill —
  any time visual asset creation is needed while building an application, this
  is the right tool. Do NOT use this skill for screenshots or non-branding
  image tasks.
---

# BrandKit — AI Image Generation for Brand Assets

Generate professional logos, icons, favicons, and banners via the BrandKit API.
The API uses Google Gemini to produce images from text prompts and returns them
as base64-encoded data. Assets are staged in a `./brandkit/` folder for review
before being deployed to the project.

## Phase 1 — Gather Brand Context

Before generating anything, understand what the user needs. The goal is to build
a clear picture of the brand so every generated asset is consistent.

### 1a. Check for existing design references

Search the project for design guides, brand docs, or existing style definitions
before asking the user questions — the answers may already be there.

Look for (in rough priority order):
- `BRAND.md`, `DESIGN.md`, `STYLE_GUIDE.md`, `brand-guidelines.*` or similar docs
- `tailwind.config.*` — check the `theme.colors` / `theme.extend.colors` section
- CSS custom properties (e.g., `--color-primary`, `--brand-*`) in global CSS files
- `theme.ts`, `theme.js`, `tokens.json`, `design-tokens.*` — design token files
- Existing image assets in `public/`, `static/`, `assets/`, `src/assets/`

If you find brand colors, fonts, or style preferences in any of these, use them
as the foundation. Mention what you found to the user: "I found your brand colors
in tailwind.config.ts — I'll use those for the assets."

### 1b. Handle reference images

If the user points to an existing image and says "make it look like this" or
"match this style", the generation API is text-only — it can't accept reference
images. Instead:

1. Read/view the reference image yourself
2. Describe its key visual elements in words: style (flat, gradient, 3D),
   color palette, composition, shapes, mood
3. Incorporate that description into the generation prompt

Tell the user: "I can't send the reference image directly to the API, but I'll
describe its style in the prompt to get a similar result."

Note: the `/modify` endpoint *does* accept an existing image for iterative
refinement — but this is for modifying previously generated assets, not for
using a reference image as a style guide.

### 1c. Ask what's needed

If the user's request is specific (e.g., "generate a blue minimalist logo for my
todo app"), you already have enough — skip to Phase 2.

If the request is open-ended (e.g., "add branding to my app" or "I need a logo"),
use the **AskUserQuestion** tool to gather preferences. This presents interactive
options the user can click on (they can always pick "Other" to give a custom
answer). The tool supports 1–4 questions per call with 2–4 options each.

**Call AskUserQuestion with these questions** (skip any the user already answered
or that the project's design files already answer):

```
Question 1:
  header: "Assets"
  question: "Which assets should I generate?"
  multiSelect: false
  options:
    - label: "Just a logo"
      description: "A single logo image"
    - label: "Logo + favicon"
      description: "Logo and favicon with standard sizes (16, 32, 180, 192, 512) plus .ico"
    - label: "Full brand kit (Recommended)"
      description: "Logo, favicon, and banner — app icon is auto-derived from the logo"

Question 2 (skip if colors found in project):
  header: "Colors"
  question: "What color direction should I go with?"
  multiSelect: false
  options:
    - label: "Blues"
      description: "Trust, professional, calm"
    - label: "Greens"
      description: "Growth, nature, health"
    - label: "Purples"
      description: "Creative, premium, modern"
    - label: "You pick"
      description: "I'll choose colors that fit the app's purpose"

Question 3 (skip if style found in project):
  header: "Style"
  question: "What visual style do you prefer?"
  multiSelect: false
  options:
    - label: "Minimal / flat"
      description: "Clean lines, solid colors, simple shapes"
    - label: "Modern / gradient"
      description: "Smooth gradients, depth, contemporary feel"
    - label: "Bold / playful"
      description: "Bright colors, fun shapes, energetic"
    - label: "Elegant / refined"
      description: "Serif fonts, muted tones, sophisticated"

Question 4:
  header: "Symbol"
  question: "What symbol or imagery should the logo use?"
  multiSelect: false
  options:
    - label: "Letter / monogram"
      description: "First letter of the app name as the icon"
    - label: "Abstract shape"
      description: "Geometric forms, swooshes, or patterns"
    - label: "You suggest"
      description: "Pick a symbol that fits the app's purpose"
```

If you need to ask about text on the logo (only when the user seems to want text),
ask in a separate follow-up call:

```
  header: "Text"
  question: "Should the logo include the app name?"
  multiSelect: false
  options:
    - label: "Icon only (Recommended)"
      description: "No text — AI text rendering can be inconsistent with letter accuracy"
    - label: "Include app name"
      description: "Add the app name — may need a few attempts to get letters right"
```

**Important:** Always default to icon-only. Only ask the text question if the
user mentions wanting text on the logo — otherwise skip it and assume icon-only.

You can split these across multiple AskUserQuestion calls if needed — for
example, ask Assets + Colors first, then Style + Symbol in a second round. But
keep the total number of rounds to 2 at most. Don't over-interview.

**Default to icon-only unless the user asks for text.** AI image generation
handles text inconsistently — letters often come out distorted or misspelled.
If the user does want text, keep it to the app name only (no taglines), and
explicitly include "with the text '[AppName]' in a clean, legible font" in the
prompt. Be upfront that text rendering may need a few attempts.

### 1d. Determine output locations

Figure out where assets should **ultimately** be deployed based on the project
structure. These are the *final destinations* — during generation, assets will
be staged in `./brandkit/` first.

| Framework / Structure     | Assets directory        |
|--------------------------|------------------------|
| Next.js / React (CRA)    | `public/`              |
| Vite                     | `public/`              |
| Django                   | `static/` or `staticfiles/` |
| Flask                    | `static/`              |
| Rails                    | `app/assets/images/`   |
| iOS / Android            | project-specific       |
| Generic / unknown        | `assets/`              |

Check for an existing assets directory first. If one exists, use it.

## Phase 2 — Generate Assets to Staging

All assets are generated into a `./brandkit/` staging folder — **never directly
to final project locations**. This gives the user a chance to review and request
changes before assets go live.

**Important — app icon = resized logo:** By default, the app icon is the logo
resized to 512x512 — do NOT generate it as a separate API call. Generating the
logo and app icon independently produces similar-but-not-identical results that
look inconsistent. Instead, generate the logo at 1024x1024 with `--sizes 512`
and rename the resized copy to your app icon. Only generate a standalone app
icon via a separate API call if the user explicitly asks for an app icon that
looks different from their logo.

### API Reference

**Base URL:** `https://brandkit-api.fly.dev`

#### Submit a generation job

```bash
curl -s -X POST https://brandkit-api.fly.dev/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "...",
    "width": 1024,
    "height": 1024,
    "format": "png",
    "background": "transparent"
  }'
```

| Field        | Type   | Default    | Constraints                      |
|-------------|--------|------------|----------------------------------|
| `prompt`     | string | required   | min 1 char                       |
| `width`      | int    | 1024       | 512–4096                         |
| `height`     | int    | 1024       | 512–4096                         |
| `format`     | string | `"png"`    | `"png"` or `"webp"`             |
| `background` | string | `"opaque"` | `"transparent"` or `"opaque"`   |

**Response (202):** `{"job_id": "...", "status": "pending", "poll_url": "/jobs/{job_id}"}`

#### Submit a modification job

```bash
curl -s -X POST https://brandkit-api.fly.dev/modify \
  -H "Content-Type: application/json" \
  -d '{
    "source_image": "<base64-encoded-image>",
    "instructions": "Change the color from blue to purple",
    "source_format": "png",
    "format": "png",
    "background": "transparent"
  }'
```

| Field           | Type   | Default    | Constraints                      |
|----------------|--------|------------|----------------------------------|
| `source_image`  | string | required   | base64-encoded source image      |
| `instructions`  | string | required   | what to change                   |
| `source_format` | string | `"png"`    | `"png"` or `"webp"`             |
| `width`         | int    | null       | 512–4096, null = keep source dims |
| `height`        | int    | null       | 512–4096, null = keep source dims |
| `format`        | string | `"png"`    | `"png"` or `"webp"`             |
| `background`    | string | `"opaque"` | `"transparent"` or `"opaque"`   |

**Response (202):** `{"job_id": "...", "status": "pending", "poll_url": "/jobs/{job_id}"}`

#### Poll for result

```bash
curl -s https://brandkit-api.fly.dev/jobs/{job_id}
```

Poll every 3–5 seconds. Statuses: `pending` → `processing` → `completed` | `failed`.

When completed, `result.image_data` contains the base64-encoded image. Decode
and save it.

### Helper Script

Use the bundled `scripts/generate_asset.py` instead of manual curl + polling.
It handles submit → poll → decode → save in one command.

**Important:** Use `python3` on macOS/Linux and `python` on Windows. Check which
is available on the current platform before running.

#### Generate a new image

```bash
python3 <SKILL_DIR>/scripts/generate_asset.py \
  --prompt "A flat, minimal app icon of a lightning bolt in purple and white" \
  --output ./brandkit/logo.png \
  --width 512 --height 512 \
  --format png \
  --background transparent
```

#### Modify an existing image

```bash
python3 <SKILL_DIR>/scripts/generate_asset.py \
  --source ./brandkit/logo.png \
  --instructions "Change the color scheme to deeper blue tones" \
  --output ./brandkit/logo.png \
  --format png \
  --background transparent
```

When `--source` is provided, the script reads the file, base64-encodes it, and
sends it to `/modify` instead of `/generate`. Width/height default to the source
image dimensions if not specified.

#### Multi-size icon generation

Use `--sizes` to generate one image and resize it to multiple sizes in a single
call. Ideal for favicons and app icons:

```bash
python3 <SKILL_DIR>/scripts/generate_asset.py \
  --prompt "A bold, simple checkmark icon in blue, recognizable at small sizes" \
  --output ./brandkit/favicon.png \
  --width 512 --height 512 \
  --format png \
  --background transparent \
  --sizes 16,32,180,192,512
```

This generates at 512x512, then creates resized copies:
`favicon-16x16.png`, `favicon-32x32.png`, `favicon-180x180.png`,
`favicon-192x192.png`, and keeps the original as `favicon.png` (512x512).

#### ICO file generation

Add `--ico` to also produce a `.ico` file combining the 16x16 and 32x32 sizes
(requires `--sizes` to include 16 and 32):

```bash
python3 <SKILL_DIR>/scripts/generate_asset.py \
  --prompt "A bold, simple checkmark icon in blue" \
  --output ./brandkit/favicon.png \
  --width 512 --height 512 \
  --format png \
  --background transparent \
  --sizes 16,32,180,192,512 \
  --ico
```

Replace `<SKILL_DIR>` with the absolute path to this skill's directory.
All flags except `--output` and either `--prompt` or `--source`+`--instructions`
are optional (defaults: 1024x1024, png, opaque). Exits 0 on success, 1 on failure.

### Prompt Templates by Asset Type

Use these templates as starting points. Fill in the bracketed parts with the
brand context from Phase 1. The key difference between asset types is level of
detail — favicons must be dead simple, logos can be more expressive.

**Logo (standard — icon-only, the default):**
```
A [style] logo of [subject/symbol] in [brand colors], for [app name/description].
Clean, professional, suitable for branding. No text, icon only. [composition hint]
```
Example: "A flat, minimal vector logo of an open book with a lightbulb emerging
from its pages, in teal and warm yellow, for an education platform. Clean,
professional, centered composition. No text, icon only."

**Logo (with app name — only if user explicitly wants text):**
```
A [style] logo of [subject/symbol] with the text "[AppName]" in a clean, legible
[font style] font, in [brand colors]. Professional, suitable for branding.
```
Example: "A flat, minimal vector logo of an open book with a lightbulb, with the
text 'LearnHub' in a clean, modern sans-serif font, in teal and warm yellow."

Note: text rendering is unreliable — letters may be distorted. Warn the user and
be prepared to regenerate.

**App icon (derived from logo — the default):**

Do NOT generate the app icon as a separate API call. Instead, generate the logo
at 1024x1024 with `--sizes 512` and rename the 512x512 copy to your icon file
(e.g., `mv ./brandkit/logo-512x512.png ./brandkit/icon-512.png`). This ensures
the logo and app icon are identical, just at different sizes.

**App icon (standalone — only if user explicitly requests a different icon):**
```
A [style] app icon of [simplified subject], in [brand colors], simple and
recognizable at small sizes. [shape constraint like "within a rounded square"]
```
Example: "A modern, geometric app icon of a stylized book in teal on white,
simple and recognizable at small sizes, within a rounded square."

Only use this template when the user explicitly asks for an app icon that looks
different from the logo. Compared to a logo, standalone app icons should have
fewer details and bolder shapes since they'll be viewed at small sizes on phone
screens.

**Favicon:**
```
A bold, simple [single shape/letter] in [primary brand color], minimal detail,
must be recognizable at 32x32 pixels. No text, no fine details.
```
Example: "A bold, simple lightbulb shape in teal, minimal detail, must be
recognizable at 32x32 pixels. No text, no fine details."

Favicons are the most constrained — they're viewed at 16–32px. Use a single
bold shape or letter. Avoid any detail that would blur at small sizes.

**Banner / hero image:**
```
A wide [style] banner with [background treatment] featuring [subtle brand element],
[mood/atmosphere], for [app name/description].
```
Example: "A wide, modern banner with a subtle gradient from teal to white,
featuring a small lightbulb motif on the left, clean and inviting, for LearnHub
education platform."

**Social card / OG image:**
```
A [style] social preview card for [app name], featuring [brand element] and the
text "[App Name]" in a clean [font style] font, [brand colors], professional and
eye-catching.
```
Note: text rendering is inconsistent with AI generation — keep text to one or
two short words maximum, and be prepared to iterate.

### Choosing Settings

**Dimensions — pick based on asset type:**

| Asset Type       | Width | Height | Notes                              |
|-----------------|-------|--------|------------------------------------|
| App icon         | 512   | 512    | Derived from logo resize (not generated separately) |
| Logo (standard)  | 1024  | 1024   | Square, high-res                   |
| Logo (wide)      | 2048  | 1024   | Horizontal/landscape orientation   |
| Favicon          | 512   | 512    | Generate large, resize down with --sizes |
| Banner/hero      | 2048  | 1024   | Wide format for headers            |
| Social card      | 2048  | 1024   | OG image / Twitter card            |

**Format:**
- **PNG** — Logos, icons, favicons. Supports transparency.
- **WebP** — Banners, hero images. Smaller file size.

**Background:**
- **Transparent** — Logos, icons, favicons.
- **Opaque** — Banners, hero images, social cards.

### Generating Multiple Assets

When the user wants a full brand kit, generate all assets in parallel by running
multiple script invocations simultaneously. Use the same style/color language in
every prompt for consistency. **All outputs go to `./brandkit/`.**

Example — full brand kit for "TaskFlow", a productivity app in blue tones:
```bash
# Run all of these in parallel
# Logo at 1024x1024 + auto-generate a 512x512 copy for the app icon
python3 <SKILL_DIR>/scripts/generate_asset.py \
  --prompt "A flat, minimal vector logo of a flowing checkmark in sky blue and white, for a productivity app. Clean, professional, centered composition. No text, icon only." \
  --output ./brandkit/logo.png --width 1024 --height 1024 --format png --background transparent \
  --sizes 512

python3 <SKILL_DIR>/scripts/generate_asset.py \
  --prompt "A bold, simple flowing checkmark in sky blue, minimal detail, must be recognizable at 32x32 pixels. No text, no fine details." \
  --output ./brandkit/favicon.png --width 512 --height 512 --format png --background transparent \
  --sizes 16,32,180,192,512 --ico

python3 <SKILL_DIR>/scripts/generate_asset.py \
  --prompt "A wide, modern banner with a subtle gradient from sky blue to white, featuring a small flowing checkmark on the left, clean and inviting, for TaskFlow productivity app" \
  --output ./brandkit/banner.webp --width 2048 --height 1024 --format webp --background opaque
```

After the logo generation completes, rename the resized copy to the app icon:
```bash
mv ./brandkit/logo-512x512.png ./brandkit/icon-512.png
```

## Phase 3 — Review, Iterate, and Deploy

After generating assets into `./brandkit/`, present them for user review. **Never
move assets to final locations without explicit user approval.**

### 3a. Present for review

1. **Read/display each generated image** from `./brandkit/` so the user can see
   what was created
2. **List what was generated** — show each file, its dimensions, file size, and
   intended final destination
3. **Ask for approval** using **AskUserQuestion**:

```
Question 1:
  header: "Review Assets"
  question: "Here are the generated brand assets. What would you like to do?"
  multiSelect: false
  options:
    - label: "Approve all and deploy"
      description: "Move all assets to their final project locations"
    - label: "Modify specific assets"
      description: "I'll tell you which ones to change and how"
    - label: "Regenerate all"
      description: "Start over with a different direction"
```

### 3b. Iterate on specific assets

If the user wants to modify specific assets:

1. Ask which asset(s) to change and what changes they want (or they may have
   already said, e.g., "make the logo more blue")
2. Use the `--source` + `--instructions` mode to send the existing asset back
   to the API with modification instructions:

```bash
python3 <SKILL_DIR>/scripts/generate_asset.py \
  --source ./brandkit/logo.png \
  --instructions "Change the color scheme to deeper blue tones, keep the same shape" \
  --output ./brandkit/logo.png \
  --format png --background transparent
```

3. Show the updated asset to the user
4. Ask again: approve or keep iterating? Repeat until satisfied.

For favicon modifications, regenerate the base image, then re-run the `--sizes`
and `--ico` flags to update all size variants:

```bash
python3 <SKILL_DIR>/scripts/generate_asset.py \
  --source ./brandkit/favicon.png \
  --instructions "Simplify the shape, use bolder lines" \
  --output ./brandkit/favicon.png \
  --format png --background transparent \
  --sizes 16,32,180,192,512 --ico
```

If the user wants to completely re-do an asset (not modify the existing one),
use `--prompt` instead of `--source` to generate fresh.

### 3c. Deploy approved assets

Once the user approves:

1. **Copy each file** from `./brandkit/` to its final destination. For example:
   - `./brandkit/logo.png` → `./public/logo.png`
   - `./brandkit/favicon.png` → `./public/favicon.png`
   - `./brandkit/favicon-16x16.png` → `./public/favicon-16x16.png`
   - `./brandkit/favicon.ico` → `./public/favicon.ico`
   - `./brandkit/banner.webp` → `./public/banner.webp`

2. **Update framework-specific config** if applicable (e.g., favicon links in
   `index.html`, `manifest.json` for PWA icons)

3. **Ask about cleanup**: "Assets are deployed. Want me to delete the
   `./brandkit/` staging folder, or keep it for future reference?"

## Error Handling

| Code                        | Retryable | Action                          |
|----------------------------|-----------|----------------------------------|
| `content_policy_violation` | No        | Rephrase the prompt              |
| `model_error`              | Yes       | Retry after 5 seconds            |
| `rate_limited`             | Yes       | Wait for `retry_after` seconds   |
| `timeout`                  | Yes       | Retry after 5 seconds            |

If a job fails with `retryable: true`, wait 5 seconds and retry once
automatically. If it fails with `retryable: false`, tell the user and suggest a
revised prompt.
