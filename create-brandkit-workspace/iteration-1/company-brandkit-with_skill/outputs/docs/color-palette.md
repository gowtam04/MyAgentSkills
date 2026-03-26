# Meridian Partners Color Palette

## Primary Colors

### Navy Blue
- **Hex:** #1B365D
- **RGB:** rgb(27, 54, 93)
- **HSL:** hsl(215, 55%, 24%)
- **Usage:** Main brand color. Use for headers, primary buttons, key brand elements, logo on light backgrounds, navigation bars, and footer backgrounds. This is the dominant color in the brand system.

### Gold
- **Hex:** #C5A55A
- **RGB:** rgb(197, 165, 90)
- **HSL:** hsl(42, 48%, 56%)
- **Usage:** Accent color. Use for highlights, CTAs, decorative elements, hover states, dividers, and premium callouts. Pairs with navy to convey authority and quality.

## Extended Primary Palette

### Navy Light
- **Hex:** #2A4F7F
- **RGB:** rgb(42, 79, 127)
- **Usage:** Lighter navy for hover states, secondary buttons, and secondary headings

### Navy Dark
- **Hex:** #0F2240
- **RGB:** rgb(15, 34, 64)
- **Usage:** Deeper navy for dark mode backgrounds, emphasis areas, and footer backgrounds

### Gold Light
- **Hex:** #D4BA78
- **RGB:** rgb(212, 186, 120)
- **Usage:** Lighter gold for background tints, subtle highlights, and decorative borders

### Gold Dark
- **Hex:** #A88B3D
- **RGB:** rgb(168, 139, 61)
- **Usage:** Deeper gold for text on light backgrounds, active states, and high-contrast accents

## Neutral Colors

### Charcoal (Text)
- **Hex:** #2D2D2D
- **RGB:** rgb(45, 45, 45)
- **Usage:** Body text, headings on light backgrounds. Primary text color for all content.

### Slate (Secondary Text)
- **Hex:** #5A6577
- **RGB:** rgb(90, 101, 119)
- **Usage:** Secondary text, captions, meta information, placeholder text

### Silver (Borders)
- **Hex:** #C8CDD3
- **RGB:** rgb(200, 205, 211)
- **Usage:** Dividers, borders, disabled states, subtle UI elements, table rules

### Mist (Subtle Background)
- **Hex:** #EBEDF0
- **RGB:** rgb(235, 237, 240)
- **Usage:** Card backgrounds, alternating table rows, sidebar backgrounds

### Warm White (Background)
- **Hex:** #F8F7F4
- **RGB:** rgb(248, 247, 244)
- **Usage:** Page backgrounds, card surfaces. Slightly warm to avoid sterile feel.

### Pure White
- **Hex:** #FFFFFF
- **RGB:** rgb(255, 255, 255)
- **Usage:** Content areas, modal backgrounds, input fields

## Accent / Status Colors

### Success — #2E7D4F
A muted green that complements the navy/gold palette. Use for success states, confirmations, positive indicators.

### Warning — #D4960A
A warm amber that harmonizes with the gold accent. Use for warnings, caution states, pending indicators.

### Error — #B83A3A
A muted red that maintains the professional tone. Use for errors, destructive actions, critical alerts.

### Info — #2A4F7F
Uses Navy Light for informational states, tips, and neutral alerts.

## Accessibility Notes

| Foreground | Background | Contrast Ratio | WCAG AA | WCAG AAA |
|---|---|---|---|---|
| Charcoal (#2D2D2D) | Warm White (#F8F7F4) | ~13.5:1 | Pass | Pass |
| White (#FFFFFF) | Navy (#1B365D) | ~9.2:1 | Pass | Pass |
| White (#FFFFFF) | Gold (#C5A55A) | ~2.5:1 | Fail | Fail |
| Charcoal (#2D2D2D) | Gold (#C5A55A) | ~5.4:1 | Pass | Fail |
| Navy (#1B365D) | Warm White (#F8F7F4) | ~9.0:1 | Pass | Pass |

**Note:** White text on gold does not meet WCAG AA standards. When using gold as a background, use charcoal or navy text instead. Gold is best used for decorative elements, borders, and accents rather than as a text background.

## Implementation

### CSS Custom Properties
```css
:root {
  /* Primary */
  --color-primary: #1B365D;
  --color-primary-light: #2A4F7F;
  --color-primary-dark: #0F2240;
  --color-secondary: #C5A55A;
  --color-secondary-light: #D4BA78;
  --color-secondary-dark: #A88B3D;

  /* Neutrals */
  --color-text: #2D2D2D;
  --color-text-secondary: #5A6577;
  --color-border: #C8CDD3;
  --color-surface: #EBEDF0;
  --color-background: #F8F7F4;
  --color-white: #FFFFFF;

  /* Status */
  --color-success: #2E7D4F;
  --color-warning: #D4960A;
  --color-error: #B83A3A;
  --color-info: #2A4F7F;
}
```

### Tailwind Config
```js
colors: {
  primary: {
    DEFAULT: '#1B365D',
    light: '#2A4F7F',
    dark: '#0F2240',
  },
  secondary: {
    DEFAULT: '#C5A55A',
    light: '#D4BA78',
    dark: '#A88B3D',
  },
  neutral: {
    900: '#2D2D2D',
    700: '#5A6577',
    300: '#C8CDD3',
    100: '#EBEDF0',
    50: '#F8F7F4',
  },
  success: '#2E7D4F',
  warning: '#D4960A',
  error: '#B83A3A',
  info: '#2A4F7F',
}
```

### Sass Variables
```scss
// Primary
$color-navy: #1B365D;
$color-navy-light: #2A4F7F;
$color-navy-dark: #0F2240;
$color-gold: #C5A55A;
$color-gold-light: #D4BA78;
$color-gold-dark: #A88B3D;

// Neutrals
$color-text: #2D2D2D;
$color-text-secondary: #5A6577;
$color-border: #C8CDD3;
$color-surface: #EBEDF0;
$color-background: #F8F7F4;

// Status
$color-success: #2E7D4F;
$color-warning: #D4960A;
$color-error: #B83A3A;
```
