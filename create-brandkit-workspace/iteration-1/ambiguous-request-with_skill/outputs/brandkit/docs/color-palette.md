# Bloom Color Palette

## Primary Colors

### Sage Green
- **Hex:** #8FB996
- **RGB:** rgb(143, 185, 150)
- **HSL:** hsl(130, 22%, 64%)
- **Usage:** Main brand color. Use for headers, primary buttons, key brand elements, logo on light backgrounds. Represents growth, nature, and wellness.

### Soft Lavender
- **Hex:** #C4A6C4
- **RGB:** rgb(196, 166, 196)
- **HSL:** hsl(300, 18%, 71%)
- **Usage:** Secondary brand color. Use for accents, highlights, decorative elements, hover states. Represents calm, mindfulness, and spiritual balance.

## Neutral Colors

### Deep Charcoal (Text)
- **Hex:** #2D2D2D
- **Usage:** Body text, headings on light backgrounds

### Warm White (Background)
- **Hex:** #FAF8F5
- **Usage:** Page backgrounds, card surfaces — warmer than pure white to feel more calming

### Mist Gray (Borders)
- **Hex:** #D4D0CC
- **Usage:** Dividers, borders, disabled states, subtle UI elements

## Extended Palette

### Sage Green — Light
- **Hex:** #C5DCC9
- **Usage:** Light backgrounds, card fills, subtle highlights

### Sage Green — Dark
- **Hex:** #5E8A66
- **Usage:** Dark accents, active states, emphasis

### Lavender — Light
- **Hex:** #E0D2E0
- **Usage:** Light backgrounds, secondary card fills

### Lavender — Dark
- **Hex:** #9A7B9A
- **Usage:** Dark accents, secondary emphasis

## Accent / Status Colors

### Success — #6BAF7A
### Warning — #E8C547
### Error — #D4665A

## Accessibility Notes
| Foreground | Background | Contrast Ratio | WCAG AA |
|---|---|---|---|
| Deep Charcoal (#2D2D2D) | Warm White (#FAF8F5) | ~14.5:1 | Pass |
| White (#FFFFFF) | Sage Green (#8FB996) | ~2.5:1 | Fail (use for large text or decorative only) |
| Deep Charcoal (#2D2D2D) | Sage Green Light (#C5DCC9) | ~9.2:1 | Pass |
| White (#FFFFFF) | Sage Green Dark (#5E8A66) | ~3.8:1 | Pass (large text only) |

Note: The primary sage green does not have sufficient contrast with white text for body copy. Use Deep Charcoal on sage green backgrounds, or use Sage Green Dark for text on light backgrounds.

## Implementation

### CSS Custom Properties
```css
:root {
  --color-primary: #8FB996;
  --color-primary-light: #C5DCC9;
  --color-primary-dark: #5E8A66;
  --color-secondary: #C4A6C4;
  --color-secondary-light: #E0D2E0;
  --color-secondary-dark: #9A7B9A;
  --color-text: #2D2D2D;
  --color-background: #FAF8F5;
  --color-border: #D4D0CC;
  --color-success: #6BAF7A;
  --color-warning: #E8C547;
  --color-error: #D4665A;
}
```

### Tailwind Config
```js
colors: {
  primary: { DEFAULT: '#8FB996', light: '#C5DCC9', dark: '#5E8A66' },
  secondary: { DEFAULT: '#C4A6C4', light: '#E0D2E0', dark: '#9A7B9A' },
  text: { DEFAULT: '#2D2D2D' },
  background: { DEFAULT: '#FAF8F5' },
  border: { DEFAULT: '#D4D0CC' },
  success: { DEFAULT: '#6BAF7A' },
  warning: { DEFAULT: '#E8C547' },
  error: { DEFAULT: '#D4665A' },
}
```
