---
name: create-brandkit
description: >
  Generate logos, icons, favicons, banners, and other brand/visual assets using
  the BrandKit image-generation API. Use this skill whenever the user asks you to
  create, generate, or design a logo, app icon, favicon, banner, hero image,
  brand asset, or any visual graphic for their project. Also trigger when the user
  mentions "brandkit", "brand kit", or asks for image generation for branding
  purposes. Even if the user just says "add a logo" or "I need an icon for my
  app", use this skill — any time visual asset creation is needed while building
  an application, this is the right tool. Do NOT use this skill for editing
  existing images, screenshots, or non-branding image tasks.
---

# BrandKit — AI Image Generation for Brand Assets

Generate professional logos, icons, favicons, and banners via the BrandKit API.
The API uses Google Gemini to produce images from text prompts and returns them
as base64-encoded data that you save directly to the project.

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
"match this style", the API is text-only — it can't accept reference images.
Instead:

1. Read/view the reference image yourself
2. Describe its key visual elements in words: style (flat, gradient, 3D),
   color palette, composition, shapes, mood
3. Incorporate that description into the generation prompt

Tell the user: "I can't send the reference image directly to the API, but I'll
describe its style in the prompt to get a similar result."

### 1c. Ask what's needed

If the user's request is specific (e.g., "generate a blue minimalist logo for my
todo app"), you already have enough — skip to Phase 2.

If the request is open-ended (e.g., "add branding to my app" or "I need a logo"),
ask a few short questions. Don't overwhelm — keep it to what you actually need:

1. **Which assets?** — "Do you want just a logo, or a full set (logo, favicon,
   app icon, banner)?"
2. **Style** (if not found in project) — "Any style preference? (minimal/flat,
   modern/gradient, bold/playful, elegant/serif)"
3. **Colors** (if not found in project) — "Any brand colors in mind, or should I
   pick something that fits the app?"
4. **Subject/symbol** — "Any specific symbol or imagery? (e.g., a mountain, a
   lightning bolt, the letter 'A')"
5. **Text on logo?** — "Should the logo include the app name, or be icon-only?"

Skip questions the user already answered or that the project's design files
already answer. One round of questions is enough — don't over-interview.

**Default to icon-only unless the user asks for text.** AI image generation
handles text inconsistently — letters often come out distorted or misspelled.
If the user does want text, keep it to the app name only (no taglines), and
explicitly include "with the text '[AppName]' in a clean, legible font" in the
prompt. Be upfront that text rendering may need a few attempts.

### 1d. Determine output locations

Figure out where assets should be saved based on the project structure:

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

## Phase 2 — Generate Assets

### API Reference

**Base URL:** `https://brandkit-api.fly.dev`

**Submit a job:**
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

**Poll for result:**
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

```bash
python3 <SKILL_DIR>/scripts/generate_asset.py \
  --prompt "A flat, minimal app icon of a lightning bolt in purple and white" \
  --output ./public/logo.png \
  --width 512 --height 512 \
  --format png \
  --background transparent
```

**Multi-size icon generation** — use `--sizes` to generate one image and resize
it to multiple sizes in a single call. This is ideal for favicons and app icons
that need several size variants:

```bash
python3 <SKILL_DIR>/scripts/generate_asset.py \
  --prompt "A bold, simple checkmark icon in blue, recognizable at small sizes" \
  --output ./public/favicon.png \
  --width 512 --height 512 \
  --format png \
  --background transparent \
  --sizes 16,32,180,192,512
```

This generates at 512x512, then creates resized copies:
`favicon-16x16.png`, `favicon-32x32.png`, `favicon-180x180.png`,
`favicon-192x192.png`, and keeps the original as `favicon.png` (512x512).

**ICO file generation** — add `--ico` to also produce a `.ico` file combining
the 16x16 and 32x32 sizes (requires `--sizes` to include 16 and 32):

```bash
python3 <SKILL_DIR>/scripts/generate_asset.py \
  --prompt "A bold, simple checkmark icon in blue" \
  --output ./public/favicon.png \
  --width 512 --height 512 \
  --format png \
  --background transparent \
  --sizes 16,32,180,192,512 \
  --ico
```

This creates everything above plus `favicon.ico`.

Replace `<SKILL_DIR>` with the absolute path to this skill's directory.
All flags except `--prompt` and `--output` are optional (defaults: 1024x1024,
png, opaque). Exits 0 on success, 1 on failure.

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

**App icon:**
```
A [style] app icon of [simplified subject], in [brand colors], simple and
recognizable at small sizes. [shape constraint like "within a rounded square"]
```
Example: "A modern, geometric app icon of a stylized book in teal on white,
simple and recognizable at small sizes, within a rounded square."

Compared to a logo, app icons should have fewer details and bolder shapes since
they'll be viewed at small sizes on phone screens.

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
| App icon         | 512   | 512    | Square, works for PWA/mobile       |
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
every prompt for consistency.

Example — full brand kit for "TaskFlow", a productivity app in blue tones:
```bash
# Run all of these in parallel
python3 <SKILL_DIR>/scripts/generate_asset.py \
  --prompt "A flat, minimal vector logo of a flowing checkmark in sky blue and white, for a productivity app. Clean, professional, centered composition. No text, icon only." \
  --output ./public/logo.png --width 1024 --height 1024 --format png --background transparent

python3 <SKILL_DIR>/scripts/generate_asset.py \
  --prompt "A flat, minimal app icon of a flowing checkmark in sky blue and white, simple and recognizable at small sizes, within a rounded square, for TaskFlow" \
  --output ./public/icon-512.png --width 512 --height 512 --format png --background transparent

python3 <SKILL_DIR>/scripts/generate_asset.py \
  --prompt "A bold, simple flowing checkmark in sky blue, minimal detail, must be recognizable at 32x32 pixels. No text, no fine details." \
  --output ./public/favicon.png --width 512 --height 512 --format png --background transparent \
  --sizes 16,32,180,192,512 --ico

python3 <SKILL_DIR>/scripts/generate_asset.py \
  --prompt "A wide, modern banner with a subtle gradient from sky blue to white, featuring a small flowing checkmark on the left, clean and inviting, for TaskFlow productivity app" \
  --output ./public/banner.webp --width 2048 --height 1024 --format webp --background opaque
```

## Phase 3 — Verify and Refine

After generating:

1. **Read/display the generated images** so the user can see what was created
2. **Report what was generated** — list each file, its dimensions, and file size
3. **Ask if adjustments are needed** — "How do these look? Want me to adjust
   colors, style, or regenerate any of them?"

If the user wants changes, regenerate just the specific assets with an updated
prompt. Don't regenerate everything unless asked.

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
