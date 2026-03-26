# Meridian Partners Typography Guide

## Font Stack

### Headings — Playfair Display
- **Font:** Playfair Display
- **Weights:** Bold (700) for H1-H2, Semibold (600) for H3-H4
- **Fallback:** `'Georgia', 'Times New Roman', serif`
- **Use for:** Page headings, hero text, marketing headlines, presentation titles, report headers
- **Source:** https://fonts.google.com/specimen/Playfair+Display

### Body — Source Sans 3
- **Font:** Source Sans 3
- **Weights:** Regular (400) for body text, Medium (500) for emphasis, Semibold (600) for bold UI elements
- **Fallback:** `'Helvetica Neue', 'Arial', sans-serif`
- **Use for:** Body text, paragraphs, UI labels, descriptions, navigation, form inputs, data tables
- **Source:** https://fonts.google.com/specimen/Source+Sans+3

### Monospace — JetBrains Mono
- **Font:** JetBrains Mono
- **Weights:** Regular (400), Medium (500)
- **Fallback:** `'Courier New', 'Consolas', monospace`
- **Use for:** Code snippets, data tables with numerical data, technical content, financial figures
- **Source:** https://fonts.google.com/specimen/JetBrains+Mono

## Type Scale

| Level   | Size          | Weight   | Line Height | Letter Spacing | Font          | Use Case        |
|---------|---------------|----------|-------------|----------------|---------------|-----------------|
| Display | 48px / 3rem   | Bold     | 1.1         | -0.02em        | Playfair Display | Hero headlines  |
| H1      | 36px / 2.25rem| Bold     | 1.2         | -0.01em        | Playfair Display | Page titles     |
| H2      | 28px / 1.75rem| Semibold | 1.3         | 0              | Playfair Display | Section headings|
| H3      | 22px / 1.375rem| Semibold| 1.4         | 0              | Playfair Display | Subsections     |
| H4      | 18px / 1.125rem| Medium  | 1.4         | 0              | Source Sans 3 | Card headings   |
| Body    | 16px / 1rem   | Regular  | 1.6         | 0              | Source Sans 3 | Paragraphs      |
| Small   | 14px / 0.875rem| Regular | 1.5         | 0              | Source Sans 3 | Captions        |
| Tiny    | 12px / 0.75rem| Medium   | 1.4         | 0.02em         | Source Sans 3 | Labels, badges  |

## Font Pairing Rationale

Playfair Display and Source Sans 3 create a classic serif/sans-serif pairing that reinforces Meridian Partners' brand personality. Playfair Display's high-contrast letterforms and refined details evoke tradition, authority, and intellectual rigor — essential qualities for a strategy consultancy advising executive leadership. Source Sans 3, Adobe's first open-source typeface family, provides clean readability and a professional neutrality that lets the content speak without distraction. Together, they balance gravitas (headings that command attention) with clarity (body text that communicates efficiently). This pairing is also widely supported across platforms and devices, ensuring brand consistency across digital and print touchpoints.

## Typographic Hierarchy Guidelines

### Headlines
- Use Playfair Display for all headlines (H1-H3)
- Headlines should be navy (#1B365D) on light backgrounds, white (#FFFFFF) on dark backgrounds
- Avoid using gold for headline text — reserve gold for decorative accents and dividers

### Body Text
- Use Source Sans 3 at 16px base size with 1.6 line height for optimal readability
- Body text should be charcoal (#2D2D2D) for primary content, slate (#5A6577) for secondary content
- Paragraphs should have a maximum line width of 65-75 characters for comfortable reading

### Emphasis
- **Bold:** Source Sans 3 Semibold (600) — use for emphasis within body text
- *Italic:* Source Sans 3 Italic — use sparingly for citations, technical terms, or subtle emphasis
- ALL CAPS: Source Sans 3 Medium with 0.05em letter spacing — use only for labels, badges, and category tags (never for sentences)

### Numbers & Data
- Financial figures, percentages, and tabular data should use JetBrains Mono for alignment and clarity
- Use Source Sans 3 for numbers within prose

## Implementation

### Google Fonts Import
```css
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Source+Sans+3:ital,wght@0,400;0,500;0,600;1,400&family=JetBrains+Mono:wght@400;500&display=swap');
```

### CSS Custom Properties
```css
:root {
  --font-heading: 'Playfair Display', 'Georgia', 'Times New Roman', serif;
  --font-body: 'Source Sans 3', 'Helvetica Neue', 'Arial', sans-serif;
  --font-mono: 'JetBrains Mono', 'Courier New', 'Consolas', monospace;

  /* Type scale */
  --text-display: 3rem;      /* 48px */
  --text-h1: 2.25rem;        /* 36px */
  --text-h2: 1.75rem;        /* 28px */
  --text-h3: 1.375rem;       /* 22px */
  --text-h4: 1.125rem;       /* 18px */
  --text-body: 1rem;          /* 16px */
  --text-small: 0.875rem;    /* 14px */
  --text-tiny: 0.75rem;      /* 12px */
}

h1, h2, h3 {
  font-family: var(--font-heading);
  color: #1B365D;
}

h1 { font-size: var(--text-h1); font-weight: 700; line-height: 1.2; letter-spacing: -0.01em; }
h2 { font-size: var(--text-h2); font-weight: 600; line-height: 1.3; }
h3 { font-size: var(--text-h3); font-weight: 600; line-height: 1.4; }
h4 { font-size: var(--text-h4); font-weight: 500; line-height: 1.4; font-family: var(--font-body); }

body {
  font-family: var(--font-body);
  font-size: var(--text-body);
  line-height: 1.6;
  color: #2D2D2D;
}

code, pre {
  font-family: var(--font-mono);
}
```

### Tailwind Config
```js
fontFamily: {
  heading: ['"Playfair Display"', 'Georgia', '"Times New Roman"', 'serif'],
  body: ['"Source Sans 3"', '"Helvetica Neue"', 'Arial', 'sans-serif'],
  mono: ['"JetBrains Mono"', '"Courier New"', 'Consolas', 'monospace'],
},
fontSize: {
  'display': ['3rem', { lineHeight: '1.1', letterSpacing: '-0.02em' }],
  'h1': ['2.25rem', { lineHeight: '1.2', letterSpacing: '-0.01em' }],
  'h2': ['1.75rem', { lineHeight: '1.3' }],
  'h3': ['1.375rem', { lineHeight: '1.4' }],
  'h4': ['1.125rem', { lineHeight: '1.4' }],
  'body': ['1rem', { lineHeight: '1.6' }],
  'small': ['0.875rem', { lineHeight: '1.5' }],
  'tiny': ['0.75rem', { lineHeight: '1.4', letterSpacing: '0.02em' }],
}
```

### HTML Link Tag (alternative to CSS @import)
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Source+Sans+3:ital,wght@0,400;0,500;0,600;1,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```
