# Meridian Partners — Color Palette Reference

## Primary Palette

### Meridian Navy
- **Hex:** #1B2A4A
- **RGB:** 27, 42, 74
- **HSL:** 221, 47%, 20%
- **CMYK:** 95, 75, 30, 45
- **Pantone (nearest):** Pantone 289 C
- **Role:** Primary brand color. Use for backgrounds, headlines, primary buttons, navigation bars, and any element that needs to convey authority and trust.
- **CSS Variable:** `--color-navy: #1B2A4A;`
- **Tailwind:** `navy: '#1B2A4A'`

### Meridian Gold
- **Hex:** #C8A951
- **RGB:** 200, 169, 81
- **HSL:** 44, 52%, 55%
- **CMYK:** 15, 25, 75, 5
- **Pantone (nearest):** Pantone 7405 C
- **Role:** Accent and highlight color. Use sparingly for CTAs, dividers, icon accents, hover states, and premium visual touches.
- **CSS Variable:** `--color-gold: #C8A951;`
- **Tailwind:** `gold: '#C8A951'`

---

## Secondary Palette

### Meridian Slate
- **Hex:** #2D4A7A
- **RGB:** 45, 74, 122
- **HSL:** 217, 46%, 33%
- **Role:** Secondary backgrounds, card borders, secondary buttons, hover states on navy elements.
- **CSS Variable:** `--color-slate: #2D4A7A;`

### Meridian Champagne
- **Hex:** #E8D9A0
- **RGB:** 232, 217, 160
- **HSL:** 48, 60%, 77%
- **Role:** Light gold for backgrounds, tinted sections, subtle highlights. Pairs well with navy text.
- **CSS Variable:** `--color-champagne: #E8D9A0;`

---

## Neutral Palette

### Clean White
- **Hex:** #FFFFFF
- **RGB:** 255, 255, 255
- **Role:** Backgrounds, text on dark, card surfaces.
- **CSS Variable:** `--color-white: #FFFFFF;`

### Warm White
- **Hex:** #F7F5F0
- **RGB:** 247, 245, 240
- **Role:** Page backgrounds, alternating section backgrounds. Slightly warmer than pure white for a refined feel.
- **CSS Variable:** `--color-warm-white: #F7F5F0;`

### Light Gray
- **Hex:** #E5E7EB
- **RGB:** 229, 231, 235
- **Role:** Borders, dividers, disabled states.
- **CSS Variable:** `--color-light-gray: #E5E7EB;`

### Meridian Gray
- **Hex:** #6B7280
- **RGB:** 107, 114, 128
- **Role:** Secondary text, captions, metadata, placeholder text.
- **CSS Variable:** `--color-gray: #6B7280;`

### Meridian Charcoal
- **Hex:** #2C2C2C
- **RGB:** 44, 44, 44
- **Role:** Primary body text color. Near-black for comfortable reading.
- **CSS Variable:** `--color-charcoal: #2C2C2C;`

---

## Functional Colors

### Success
- **Hex:** #2D7A4F
- **RGB:** 45, 122, 79
- **Role:** Success states, positive indicators, confirmations.

### Warning
- **Hex:** #C8A020
- **RGB:** 200, 160, 32
- **Role:** Warning states, caution indicators. Harmonizes with the gold palette.

### Error
- **Hex:** #B83C3C
- **RGB:** 184, 60, 60
- **Role:** Error states, destructive actions, alerts.

### Info
- **Hex:** #2D4A7A
- **RGB:** 45, 74, 122
- **Role:** Informational states. Uses Meridian Slate for consistency.

---

## Gradient Definitions

### Primary Gradient (Navy Depth)
```css
background: linear-gradient(135deg, #1B2A4A 0%, #2D4A7A 100%);
```
Use for hero sections, banner backgrounds, presentation slides.

### Gold Shimmer
```css
background: linear-gradient(90deg, #C8A951 0%, #E8D9A0 50%, #C8A951 100%);
```
Use sparingly for premium accents, divider lines, hover highlights.

### Dark Overlay
```css
background: linear-gradient(180deg, rgba(27, 42, 74, 0.9) 0%, rgba(27, 42, 74, 0.7) 100%);
```
Use as overlay on images to ensure text readability.

---

## Contrast Ratios (WCAG 2.1)

| Foreground | Background | Ratio | Level |
|-----------|-----------|-------|-------|
| White (#FFF) | Navy (#1B2A4A) | 12.6:1 | AAA |
| Charcoal (#2C2C2C) | White (#FFF) | 13.1:1 | AAA |
| Navy (#1B2A4A) | Warm White (#F7F5F0) | 11.4:1 | AAA |
| Gold (#C8A951) | Navy (#1B2A4A) | 4.8:1 | AA Large |
| Gold (#C8A951) | White (#FFF) | 2.5:1 | Decorative only |
| Navy (#1B2A4A) | Champagne (#E8D9A0) | 8.2:1 | AAA |

**Important:** Gold on white does not meet contrast requirements for text. Use gold only as a decorative/accent element on white backgrounds, never for readable text. For text on white, use navy or charcoal.

---

## Implementation Examples

### CSS Custom Properties
```css
:root {
  --color-navy: #1B2A4A;
  --color-gold: #C8A951;
  --color-slate: #2D4A7A;
  --color-champagne: #E8D9A0;
  --color-white: #FFFFFF;
  --color-warm-white: #F7F5F0;
  --color-light-gray: #E5E7EB;
  --color-gray: #6B7280;
  --color-charcoal: #2C2C2C;
}
```

### Tailwind Config
```javascript
colors: {
  navy: '#1B2A4A',
  gold: '#C8A951',
  slate: '#2D4A7A',
  champagne: '#E8D9A0',
  'warm-white': '#F7F5F0',
  charcoal: '#2C2C2C',
}
```
