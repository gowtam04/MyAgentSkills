---
name: create-brandkit
description: >
  Generate, modify, and iterate on logos, icons, favicons, banners, and other
  brand/visual assets using the BrandKit image-generation API. Also create
  comprehensive company brand kits including logo variations, brand guidelines,
  color palette documentation, typography recommendations, social media assets,
  business card concepts, and brand patterns. Use this skill whenever the user
  asks to create, generate, design, edit, or refine a logo, app icon, favicon,
  banner, hero image, brand asset, or any visual graphic. Also trigger for
  company branding, corporate identity, brand guidelines, brand book, visual
  identity system, style guide, color palette, or typography recommendations.
  Trigger on "brandkit", "brand kit", or any branding-related image/document
  generation. Even if the user just says "add a logo", "I need an icon for my
  app", "create brand guidelines", or "set up our company branding", use this
  skill. Do NOT use this skill for screenshots or non-branding image tasks.
---

# BrandKit — AI Brand Asset Generation

Generate professional brand assets via the BrandKit API. This skill handles two
modes:

- **App / Product branding** — Logo, favicon, app icon, and banner for an app or
  product. Quick and focused.
- **Company brand kit** — A comprehensive brand identity system: logo variations
  (primary, monochrome, reversed), brand guidelines document, color palette
  specification, typography guide, social media assets, business card concepts,
  brand patterns, and more.

The API uses Google Gemini to produce images from text prompts and returns them
as base64-encoded data. Text documents (brand guidelines, color palette,
typography guide) are written directly by you — no API call needed. All assets
are staged in a `./brandkit/` folder for review before being deployed.

## Phase 1 — Gather Brand Context

Before generating anything, understand what the user needs. The goal is to build
a clear picture of the brand so every generated asset is consistent.

### 1a. Determine brand kit type

First, figure out whether this is an app/product branding request or a company
brand kit request. Often the user's request makes this obvious:

- **Clearly app/product:** "add a logo to my app", "I need a favicon for my
  website", "generate an icon for TaskFlow" → proceed to step 1b (app flow)
- **Clearly company:** "create brand guidelines for my company", "I need a full
  brand kit for Meridian Partners", "set up our corporate identity", "design
  our company branding" → proceed to step 1f (company flow)
- **Ambiguous:** "I need branding", "help me with brand assets", "create a
  brand kit" → ask the user

If ambiguous, use **AskUserQuestion**:

```
Question 1:
  header: "Brand Kit"
  question: "What type of brand kit do you need?"
  multiSelect: false
  options:
    - label: "App / Product branding"
      description: "Logo, favicon, app icon, and banner for an app or product"
    - label: "Company brand kit"
      description: "Full identity system: logo variations, brand guidelines, color palette, typography, social media assets, and more"
    - label: "Just one asset"
      description: "I need a single specific image (logo, icon, banner, etc.)"
```

"Just one asset" follows the app/product flow but generates only the requested
asset.

---

## App / Product Flow (steps 1b–1e, Phase 2a, Phase 3a)

Use this flow when the user wants branding for an app, product, or just needs
individual assets.

### 1b. Check for existing design references

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

### 1c. Handle reference images

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

### 1d. Ask what's needed

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

### 1e. Determine output locations

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

---

## Company Brand Kit Flow (steps 1f–1h, Phase 2b, Phase 3b)

Use this flow when the user wants a comprehensive brand identity system for a
company or organization. This produces both visual assets (via the API) and text
documents (brand guidelines, color palette, typography guide) that you write
directly.

### 1f. Check for existing brand context

Same as step 1b — search the project for design guides, brand docs, existing
colors, and style definitions. For company kits, also look for:
- Company "about" pages or mission statements in the codebase
- Existing brand assets that should inform the new kit
- README or docs that describe the company's purpose

If you find relevant context, use it and tell the user what you found.

### 1g. Gather company brand context

If the user's request already includes enough detail (company name, industry,
style preferences), skip straight to the deliverables question. Otherwise, use
**AskUserQuestion** to gather context. Keep it to 2 rounds maximum.

**Round 1 (up to 4 questions — skip any the user already answered):**

```
Question 1:
  header: "Industry"
  question: "What industry or sector is the company in?"
  multiSelect: false
  options:
    - label: "Technology / SaaS"
      description: "Software, cloud services, tech products"
    - label: "Professional services"
      description: "Consulting, legal, finance, accounting"
    - label: "Creative / Media"
      description: "Design, marketing, entertainment, publishing"
    - label: "E-commerce / Retail"
      description: "Online stores, consumer products, marketplaces"

Question 2 (skip if colors found in project):
  header: "Colors"
  question: "What color direction fits the brand?"
  multiSelect: false
  options:
    - label: "Blues / Navy"
      description: "Trust, authority, professionalism"
    - label: "Greens / Teal"
      description: "Growth, sustainability, wellness"
    - label: "Dark / Monochrome"
      description: "Sophistication, luxury, timelessness"
    - label: "You pick"
      description: "I'll choose colors that fit the industry and brand personality"

Question 3:
  header: "Personality"
  question: "How should the brand feel?"
  multiSelect: false
  options:
    - label: "Professional"
      description: "Established, trustworthy, formal"
    - label: "Modern"
      description: "Forward-thinking, dynamic, innovative"
    - label: "Friendly"
      description: "Warm, approachable, conversational"
    - label: "Premium"
      description: "Exclusive, refined, high-end"

Question 4:
  header: "Deliverables"
  question: "Which deliverables do you need?"
  multiSelect: true
  options:
    - label: "Core brand kit (Recommended)"
      description: "Logo variations + brand guidelines + color palette + typography guide"
    - label: "Social media assets"
      description: "Profile pictures and cover images for LinkedIn, X, Facebook, Instagram"
    - label: "Business collateral"
      description: "Business card concept, email signature layout, letterhead concept"
    - label: "Brand patterns"
      description: "Repeatable textures and visual elements for backgrounds"
```

**Round 2 (only if needed — skip if already clear):**

```
Question 1:
  header: "Symbol"
  question: "What symbol or imagery should the logo use?"
  multiSelect: false
  options:
    - label: "Lettermark"
      description: "Company initials as the primary mark"
    - label: "Abstract mark"
      description: "Geometric or abstract shape representing the brand"
    - label: "Wordmark"
      description: "The company name as the logo (text rendering may need iteration)"
    - label: "You suggest"
      description: "Recommend a symbol based on the brand personality and industry"

Question 2 (only if social media was selected):
  header: "Platforms"
  question: "Which social platforms do you need assets for?"
  multiSelect: true
  options:
    - label: "LinkedIn"
      description: "Profile picture (400x400) and banner (1584x396)"
    - label: "X / Twitter"
      description: "Profile picture (400x400) and header (1500x500)"
    - label: "Facebook"
      description: "Profile picture (170x170) and cover (820x312)"
    - label: "Instagram"
      description: "Profile picture (320x320)"
```

### 1h. Determine company kit output locations

For company brand kits, assets are staged in `./brandkit/` with subdirectories:

```
./brandkit/
  logos/              # Primary, monochrome, reversed, icon-mark
  social/             # Platform-specific profile pics and covers
  collateral/         # Business card, email signature, letterhead concepts
  patterns/           # Brand patterns and textures
  docs/               # brand-guidelines.md, color-palette.md, typography-guide.md
```

Final deployment destinations follow the same framework logic as step 1e. Text
documents in `docs/` typically stay at the project root or in a `docs/` or
`brand/` directory — ask the user if unclear.

---

## Phase 2 — Generate Assets to Staging

All assets are generated into a `./brandkit/` staging folder — **never directly
to final project locations**. This gives the user a chance to review and request
changes before assets go live.

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

### Phase 2a — App / Product Asset Generation

**Important — app icon = resized logo:** By default, the app icon is the logo
resized to 512x512 — do NOT generate it as a separate API call. Generating the
logo and app icon independently produces similar-but-not-identical results that
look inconsistent. Instead, generate the logo at 1024x1024 with `--sizes 512`
and rename the resized copy to your app icon. Only generate a standalone app
icon via a separate API call if the user explicitly asks for an app icon that
looks different from their logo.

When the user wants a full app brand kit, generate all assets in parallel by
running multiple script invocations simultaneously. Use the same style/color
language in every prompt for consistency. **All outputs go to `./brandkit/`.**

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

### Phase 2b — Company Brand Kit Generation

Company brand kits involve both image generation (via the API) and text document
creation (written directly by you). The key principle is **consistency** — every
asset should feel like it belongs to the same brand.

#### Generation order

Generate assets in this order because later assets depend on earlier ones:

1. **Primary logo** — Generate first. Everything else derives from or references it.
   Generate at 1024x1024 with `--sizes 512` to also get an icon-mark copy.
2. **Logo variations** — Use `/modify` on the primary logo (run in parallel):
   - Monochrome (black)
   - Reversed (white)
   - Icon-only mark (if primary includes text)
3. **Favicon** — Generate separately (favicons need to be ultra-simplified)
4. **Social media covers** — Generate in parallel (one per platform)
5. **Social media profile pics** — Resize icon-mark with `--sizes`, not separate generation
6. **Business collateral** — Business card, email signature, letterhead concepts (parallel)
7. **Brand patterns** — Repeatable textures (parallel with step 6)
8. **Text documents** — Write brand guidelines, color palette, and typography guide.
   Start writing these after the primary logo is generated so you can view it and
   extract the actual colors used.

After generating the primary logo, **read/view it** to identify the exact colors,
shapes, and style. Use these observations to:
- Write accurate hex codes in the color palette document
- Ensure all subsequent image prompts reference the same visual language
- Describe the logo accurately in the brand guidelines

#### Company-specific prompt templates

**Logo variations via /modify** — always derive from the primary logo, never
generate independently. This ensures perfect consistency.

Monochrome:
```bash
python3 <SKILL_DIR>/scripts/generate_asset.py \
  --source ./brandkit/logos/primary-logo.png \
  --instructions "Convert this logo to a single-color monochrome version using only black (#000000). Remove all color — render the entire logo in solid black on a transparent background. Maintain the exact same shape and proportions." \
  --output ./brandkit/logos/monochrome-logo.png \
  --format png --background transparent
```

Reversed (white):
```bash
python3 <SKILL_DIR>/scripts/generate_asset.py \
  --source ./brandkit/logos/primary-logo.png \
  --instructions "Convert this logo to an all-white version (#FFFFFF) suitable for dark backgrounds. Remove all color — render the entire logo in solid white on a transparent background. Maintain the exact same shape and proportions." \
  --output ./brandkit/logos/reversed-logo.png \
  --format png --background transparent
```

Icon-only (only if primary logo contains text):
```bash
python3 <SKILL_DIR>/scripts/generate_asset.py \
  --source ./brandkit/logos/primary-logo.png \
  --instructions "Remove all text from this logo, keeping only the icon/symbol/mark element. Center the remaining icon on a transparent background." \
  --output ./brandkit/logos/icon-mark.png \
  --format png --background transparent
```

**Social media cover images** — generate one per platform with brand-consistent
prompts. The API requires dimensions between 512–4096, so use the nearest valid
dimensions:

| Platform   | Profile        | Cover/Banner                    |
|-----------|----------------|---------------------------------|
| LinkedIn   | 512x512 (resize) | 2048x512 (closest to 1584x396)  |
| X/Twitter  | 512x512 (resize) | 2048x682 (closest to 1500x500)  |
| Facebook   | 512x512 (resize) | 2048x780 (closest to 820x312 scaled up) |
| Instagram  | 512x512 (resize) | N/A                             |

Cover image prompt template:
```
A wide [style] banner for [company name], a [industry] company. [Brand colors]
color scheme, [mood] atmosphere, featuring [subtle brand element or abstract
shapes consistent with the logo]. Professional, clean, suitable for [platform].
No text, no logos — just branded background art.
```

Profile pictures — resize the icon-mark, don't generate separately:
```bash
python3 <SKILL_DIR>/scripts/generate_asset.py \
  --source ./brandkit/logos/icon-mark.png \
  --instructions "Keep this icon exactly as-is" \
  --output ./brandkit/social/profile.png \
  --format png --background transparent \
  --sizes 170,320,400,512
```

Or simply copy and resize the icon-mark using the `--sizes` flag on the original
logo generation.

**Business card concept:**
```
A [style] business card design for [company name], a [industry] company. Layout
features the company logo mark in [brand colors]. Show the front face of the
card. Use thin horizontal lines as placeholders where name, title, phone, email,
and address would go — do NOT attempt to render actual text characters. Clean,
professional layout with [brand style] decorative elements.
```

Generate at 2048x1200 (standard business card proportions) with opaque background.

AI image generation renders text unreliably, so business card concepts should use
placeholder lines instead of real text. This gives the user a layout/design
concept, not a print-ready card. Be upfront about this limitation.

**Email signature concept:**
```
A [style] email signature layout for [company name]. Horizontal layout with a
small logo mark on the left, thin horizontal lines as placeholders for name,
title, and contact info on the right. [Brand colors] accent line or divider.
Minimal, professional. No actual text — use placeholder lines only.
```

Generate at 1200x512 with opaque background (white or light brand color).

**Letterhead concept:**
```
A [style] letterhead design for [company name]. Portrait/vertical layout with
the company logo mark at the top, [brand colors] accent elements (subtle header
bar, footer line, or corner detail). Clean, professional, mostly white space for
content. No actual text — just the branded frame/template.
```

Generate at 2048x2800 (approximate letter proportions) with opaque background.

**Brand pattern/texture:**
```
A seamless, repeatable pattern using [brand element: abstract shapes / geometric
forms / subtle motifs inspired by the logo] in [brand colors, muted/subtle
variants]. [Style] aesthetic, professional, subtle enough for backgrounds. The
pattern should tile seamlessly.
```

Generate at 1024x1024 with opaque background.

#### Example — full company brand kit generation

For "Meridian Partners", a B2B strategy consultancy in navy/gold tones:

```bash
# Step 1: Primary logo (run first — everything else depends on this)
python3 <SKILL_DIR>/scripts/generate_asset.py \
  --prompt "A professional, modern logo of an abstract compass rose with clean geometric lines, in navy blue and gold, for a B2B strategy consultancy. Sophisticated, authoritative, centered composition. No text, icon only." \
  --output ./brandkit/logos/primary-logo.png \
  --width 1024 --height 1024 --format png --background transparent \
  --sizes 512

# Rename 512 copy to icon-mark
mv ./brandkit/logos/primary-logo-512x512.png ./brandkit/logos/icon-mark.png

# Step 2-7: Run all of these in parallel after step 1 completes

# Logo variations (via /modify)
python3 <SKILL_DIR>/scripts/generate_asset.py \
  --source ./brandkit/logos/primary-logo.png \
  --instructions "Convert to solid black monochrome on transparent background. Maintain exact shape." \
  --output ./brandkit/logos/monochrome-logo.png \
  --format png --background transparent

python3 <SKILL_DIR>/scripts/generate_asset.py \
  --source ./brandkit/logos/primary-logo.png \
  --instructions "Convert to solid white on transparent background. Maintain exact shape." \
  --output ./brandkit/logos/reversed-logo.png \
  --format png --background transparent

# Favicon
python3 <SKILL_DIR>/scripts/generate_asset.py \
  --prompt "A bold, simple compass rose shape in navy blue, minimal detail, geometric, must be recognizable at 32x32 pixels. No text, no fine details." \
  --output ./brandkit/logos/favicon.png \
  --width 512 --height 512 --format png --background transparent \
  --sizes 16,32,180,192,512 --ico

# Social covers
python3 <SKILL_DIR>/scripts/generate_asset.py \
  --prompt "A wide, sophisticated banner with a subtle gradient from navy blue to dark blue-gray, featuring subtle geometric compass lines, professional and authoritative, for a B2B consultancy. No text." \
  --output ./brandkit/social/linkedin-cover.png \
  --width 2048 --height 512 --format png --background opaque

python3 <SKILL_DIR>/scripts/generate_asset.py \
  --prompt "A wide, sophisticated banner with a subtle gradient from navy blue to dark blue-gray, featuring subtle geometric compass lines, professional and authoritative, for a B2B consultancy. No text." \
  --output ./brandkit/social/twitter-header.png \
  --width 2048 --height 682 --format png --background opaque

# Business card
python3 <SKILL_DIR>/scripts/generate_asset.py \
  --prompt "A sophisticated business card design for a strategy consultancy. Navy blue and gold color scheme. Small compass logo mark in upper left. Thin horizontal lines as placeholders for name, title, phone, email. Gold accent line divider. No actual text characters — use placeholder lines only." \
  --output ./brandkit/collateral/business-card.png \
  --width 2048 --height 1200 --format png --background opaque

# Brand pattern
python3 <SKILL_DIR>/scripts/generate_asset.py \
  --prompt "A seamless, repeatable geometric pattern using subtle compass-inspired angular lines in very light navy blue on white. Minimal, professional, suitable for document backgrounds. The pattern should tile seamlessly." \
  --output ./brandkit/patterns/brand-pattern.png \
  --width 1024 --height 1024 --format png --background opaque
```

After all image generation completes, write the text documents (see next section).

#### Text documents

These are written directly by you using the **Write** tool — no API call needed.
Write them after the primary logo is generated so you can view the logo and
extract accurate colors.

**How to determine colors:** After the primary logo is generated, read/view the
image file. Identify the dominant colors and describe them. Choose specific hex
codes that match what you observe. If the user specified colors (e.g., "navy and
gold"), use standard values for those colors (e.g., navy → #1B365D, gold → #C5A55A)
and adjust based on what the generated image actually looks like.

##### Brand Guidelines (`./brandkit/docs/brand-guidelines.md`)

Write a comprehensive brand guidelines document using this structure:

```markdown
# [Company Name] Brand Guidelines

## Brand Overview
[2-3 sentences about the company, its mission, and what the brand represents.
Draw from what the user told you about the company.]

## Brand Values
- **[Value 1]:** [Brief explanation]
- **[Value 2]:** [Brief explanation]
- **[Value 3]:** [Brief explanation]
[Derive these from the industry, personality, and any context the user provided.]

## Logo

### Primary Logo
The primary logo is the default mark for [Company Name]. Use it in most contexts
on light backgrounds.

### Logo Variations
| Variation | Use Case | File |
|---|---|---|
| Primary (full color) | Default usage on light backgrounds | `logos/primary-logo.png` |
| Monochrome (black) | Single-color printing, embossing, fax | `logos/monochrome-logo.png` |
| Reversed (white) | Dark backgrounds, photography overlays | `logos/reversed-logo.png` |
| Icon mark | Social profiles, favicons, app icons, small spaces | `logos/icon-mark.png` |

### Logo Usage Rules
- Maintain clear space around the logo equal to the height of the mark
- Minimum display size: 32px height for digital, 0.5" for print
- Do not stretch, rotate, or distort the logo
- Do not change the logo colors outside the approved palette
- Do not place on busy backgrounds without sufficient contrast
- Do not add effects (drop shadows, outlines, gradients, bevels)

## Color Palette
See [Color Palette](./color-palette.md) for full specifications with hex codes,
RGB values, and usage guidelines.

## Typography
See [Typography Guide](./typography-guide.md) for font recommendations, type
scale, and implementation details.

## Voice & Tone
- **Tone:** [Derive from brand personality — e.g., "Confident and professional,
  but not stiff. Knowledgeable without being condescending."]
- **Writing style:** [e.g., "Clear, concise, and direct. Favor active voice."]
- **Avoid:** [e.g., "Jargon without explanation, overly casual language, hyperbole"]

## Asset Inventory
[List all generated assets with their file paths and intended use]
```

Fill in all bracketed content with actual values based on the user's company,
industry, and brand personality. Don't leave placeholders.

##### Color Palette (`./brandkit/docs/color-palette.md`)

```markdown
# [Company Name] Color Palette

## Primary Colors

### [Primary Color Name] (e.g., "Navy Blue")
- **Hex:** #XXXXXX
- **RGB:** rgb(X, X, X)
- **HSL:** hsl(X, X%, X%)
- **Usage:** Main brand color. Use for headers, primary buttons, key brand elements,
  logo on light backgrounds.

### [Secondary Color Name] (e.g., "Gold")
- **Hex:** #XXXXXX
- **RGB:** rgb(X, X, X)
- **HSL:** hsl(X, X%, X%)
- **Usage:** Accent color. Use for highlights, CTAs, decorative elements, hover states.

## Neutral Colors

### Dark (Text)
- **Hex:** #XXXXXX
- **Usage:** Body text, headings on light backgrounds

### Light (Background)
- **Hex:** #XXXXXX
- **Usage:** Page backgrounds, card surfaces

### Mid (Borders)
- **Hex:** #XXXXXX
- **Usage:** Dividers, borders, disabled states, subtle UI elements

## Accent / Status Colors

### Success — #XXXXXX
### Warning — #XXXXXX
### Error — #XXXXXX

## Accessibility Notes
| Foreground | Background | Contrast Ratio | WCAG AA |
|---|---|---|---|
| Dark text | Light bg | ~X:1 | Pass/Fail |
| White text | Primary bg | ~X:1 | Pass/Fail |

[Include 2-3 of the most important combinations. Estimate contrast ratios based
on the color values — be honest if a combination may not meet AA standards.]

## Implementation

### CSS Custom Properties
```css
:root {
  --color-primary: #XXXXXX;
  --color-secondary: #XXXXXX;
  --color-text: #XXXXXX;
  --color-background: #XXXXXX;
  --color-border: #XXXXXX;
  --color-success: #XXXXXX;
  --color-warning: #XXXXXX;
  --color-error: #XXXXXX;
}
```

### Tailwind Config
```js
colors: {
  primary: { DEFAULT: '#XXXXXX', light: '#XXXXXX', dark: '#XXXXXX' },
  secondary: { DEFAULT: '#XXXXXX', light: '#XXXXXX', dark: '#XXXXXX' },
  // ... neutrals, accents
}
```
```

Replace all `#XXXXXX` with actual hex codes derived from viewing the generated
logo and the user's color preferences. Include light and dark variants of primary
and secondary colors for the Tailwind config.

##### Typography Guide (`./brandkit/docs/typography-guide.md`)

```markdown
# [Company Name] Typography Guide

## Font Stack

### Headings — [Font Name]
- **Font:** [Google Font name]
- **Weights:** Bold (700) for H1-H2, Semibold (600) for H3-H4
- **Fallback:** [system font stack, e.g., `'Georgia', serif`]
- **Use for:** Page headings, hero text, marketing headlines
- **Source:** [Google Fonts URL]

### Body — [Font Name]
- **Font:** [Google Font name]
- **Weights:** Regular (400) for body text, Medium (500) for emphasis
- **Fallback:** [system font stack, e.g., `'Helvetica Neue', sans-serif`]
- **Use for:** Body text, paragraphs, UI labels, descriptions
- **Source:** [Google Fonts URL]

### Monospace — [Font Name]
- **Font:** [monospace font name]
- **Fallback:** `'Courier New', monospace`
- **Use for:** Code snippets, data tables, technical content

## Type Scale

| Level   | Size          | Weight   | Line Height | Letter Spacing | Use Case        |
|---------|---------------|----------|-------------|----------------|-----------------|
| Display | 48px / 3rem   | Bold     | 1.1         | -0.02em        | Hero headlines  |
| H1      | 36px / 2.25rem| Bold     | 1.2         | -0.01em        | Page titles     |
| H2      | 28px / 1.75rem| Semibold | 1.3         | 0              | Section headings|
| H3      | 22px / 1.375rem| Semibold| 1.4         | 0              | Subsections     |
| H4      | 18px / 1.125rem| Medium  | 1.4         | 0              | Card headings   |
| Body    | 16px / 1rem   | Regular  | 1.6         | 0              | Paragraphs      |
| Small   | 14px / 0.875rem| Regular | 1.5         | 0              | Captions        |
| Tiny    | 12px / 0.75rem| Medium   | 1.4         | 0.02em         | Labels, badges  |

## Font Pairing Rationale
[2-3 sentences explaining why these fonts complement the brand personality and
each other. Reference the brand values.]

## Implementation

```css
@import url('https://fonts.googleapis.com/css2?family=[HeadingFont]:wght@400;600;700&family=[BodyFont]:wght@400;500&display=swap');

:root {
  --font-heading: '[HeadingFont]', [fallback];
  --font-body: '[BodyFont]', [fallback];
  --font-mono: '[MonoFont]', monospace;
}
```
```

**Font pairing recommendations by brand personality:**
- **Professional / Corporate:** Merriweather + Inter, Playfair Display + Source Sans 3
- **Modern / Innovative:** Outfit + DM Sans, Space Grotesk + Inter
- **Friendly / Approachable:** Nunito + Open Sans, Quicksand + Lato
- **Premium / Luxury:** Playfair Display + Lato, Cormorant Garamond + Montserrat

Choose the pairing that best matches the brand personality and explain your choice
in the rationale section.

---

## Phase 3 — Review, Iterate, and Deploy

After generating assets into `./brandkit/`, present them for user review. **Never
move assets to final locations without explicit user approval.**

### Phase 3a — App / Product Review

1. **Read/display each generated image** from `./brandkit/` so the user can see
   what was created
2. **List what was generated** — show each file, its dimensions, file size, and
   intended final destination
3. **Ask for approval** using **AskUserQuestion**:

```
Question 1:
  header: "Review"
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

#### Iterate on specific assets

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

#### Deploy approved app assets

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

### Phase 3b — Company Brand Kit Review

Present the company brand kit grouped by category so it's easy to evaluate:

1. **Logos** — Show all logo variations together (primary, monochrome, reversed,
   icon-mark) so the user can see them side by side
2. **Social media** — Show profile pics and covers grouped by platform
3. **Business collateral** — Show business card, email signature, letterhead concepts
4. **Brand patterns** — Show pattern/texture assets
5. **Documents** — Summarize the key points from each text document:
   - "Your primary brand color is #1B365D (Navy), secondary is #C5A55A (Gold)"
   - "Font pairing: Playfair Display for headings, Inter for body text"
   - "Brand guidelines cover logo usage rules, voice & tone, and asset inventory"

6. **Ask for approval** using **AskUserQuestion**:

```
Question 1:
  header: "Review"
  question: "Here's your complete brand kit. What would you like to do?"
  multiSelect: false
  options:
    - label: "Approve all and deploy"
      description: "Move all assets and documents to their final locations"
    - label: "Modify images"
      description: "I'll tell you which images to change and how"
    - label: "Revise documents"
      description: "I'll tell you what to update in the guidelines, palette, or typography"
    - label: "Regenerate everything"
      description: "Start over with a different direction"
```

#### Iterate on company kit assets

**For image modifications:** Same as app flow — use `--source` + `--instructions`
to modify specific images. If a logo variation is modified, remember to re-derive
dependent assets (monochrome, reversed, profile pics) from the updated primary.

**For document revisions:** The user may want to change colors, fonts, wording,
or add sections. Edit the relevant markdown file directly based on their feedback.

**For logo changes that cascade:** If the primary logo changes, you need to:
1. Re-generate monochrome and reversed variations via `/modify`
2. Re-derive the icon-mark
3. Re-resize profile pictures
4. Re-view the new logo to update color values in the palette document
5. Update the brand guidelines if the logo description changed

#### Deploy approved company kit

Once the user approves:

1. **Image assets** — Copy from `./brandkit/logos/` to the project's assets
   directory (same framework detection as step 1e)
2. **Social media assets** — Ask the user where these should go. Often they're
   downloaded/uploaded manually rather than deployed to the app. Default: keep
   in `./brandkit/social/` for the user to grab.
3. **Business collateral** — Same as social — keep in staging for download unless
   the user specifies a destination
4. **Brand patterns** — Copy to assets directory if the user wants them in the app
5. **Text documents** — Copy from `./brandkit/docs/` to the project root, `docs/`,
   or `brand/` directory. Ask if unclear.
6. **Optional: update project config** — If the project has `tailwind.config.*`,
   offer to add the brand colors from the palette. If there's a global CSS file,
   offer to add the CSS custom properties. If there's an `index.html`, offer to
   update favicon links.
7. **Ask about cleanup**: "Brand kit is deployed. Want me to keep the
   `./brandkit/` staging folder as a reference, or remove it?"

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
