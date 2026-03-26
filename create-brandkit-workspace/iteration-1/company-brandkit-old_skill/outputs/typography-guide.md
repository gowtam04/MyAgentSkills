# Meridian Partners — Typography Guide

## Overview

Meridian Partners uses a two-typeface system that pairs a refined serif for headlines with a clean sans-serif for body copy. This combination projects authority and expertise (serif) while maintaining clarity and modernity (sans-serif).

---

## Primary Typeface: Playfair Display

**Source:** [Google Fonts](https://fonts.google.com/specimen/Playfair+Display)
**Classification:** Transitional serif / Display serif
**License:** SIL Open Font License

### Usage
- Headlines (H1, H2, H3)
- The "Meridian Partners" wordmark
- Pull quotes and feature callouts
- Presentation slide titles
- Report and white paper titles

### Recommended Weights
| Weight | CSS Value | Usage |
|--------|-----------|-------|
| Regular | 400 | Subheadings (H3), pull quotes |
| Bold | 700 | Headlines (H1, H2), wordmark |

### CSS Import
```html
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&display=swap" rel="stylesheet">
```

### Font Stack
```css
font-family: "Playfair Display", Georgia, "Times New Roman", Times, serif;
```

### Character
Playfair Display conveys tradition, authority, and refinement. Its high contrast and elegant proportions align with the premium positioning of Meridian Partners. It should be used at larger sizes (20px+) where its fine details are visible.

---

## Secondary Typeface: Inter

**Source:** [Google Fonts](https://fonts.google.com/specimen/Inter)
**Classification:** Geometric sans-serif
**License:** SIL Open Font License

### Usage
- Body copy and paragraphs
- Navigation and menus
- Buttons and form elements
- Captions, labels, and metadata
- Data tables and charts
- Email communications

### Recommended Weights
| Weight | CSS Value | Usage |
|--------|-----------|-------|
| Regular | 400 | Body copy, descriptions |
| Medium | 500 | Emphasized body text, subheadings in body context |
| Semibold | 600 | Buttons, labels, H4 headings, navigation |

### CSS Import
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
```

### Font Stack
```css
font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
```

### Character
Inter was designed specifically for screens, with excellent readability at all sizes. Its neutral, professional tone complements Playfair Display without competing for attention.

---

## Type Scale

### Desktop

| Level | Font | Size | Weight | Line Height | Letter Spacing | Color |
|-------|------|------|--------|-------------|----------------|-------|
| H1 | Playfair Display | 48px (3rem) | 700 | 1.2 | -0.02em | Navy #1B2A4A |
| H2 | Playfair Display | 36px (2.25rem) | 700 | 1.25 | -0.01em | Navy #1B2A4A |
| H3 | Playfair Display | 28px (1.75rem) | 400 | 1.3 | 0 | Navy #1B2A4A |
| H4 | Inter | 20px (1.25rem) | 600 | 1.4 | 0 | Navy #1B2A4A |
| H5 | Inter | 16px (1rem) | 600 | 1.5 | 0.02em | Navy #1B2A4A |
| Body Large | Inter | 18px (1.125rem) | 400 | 1.65 | 0 | Charcoal #2C2C2C |
| Body | Inter | 16px (1rem) | 400 | 1.6 | 0 | Charcoal #2C2C2C |
| Body Small | Inter | 14px (0.875rem) | 400 | 1.5 | 0 | Gray #6B7280 |
| Caption | Inter | 12px (0.75rem) | 400 | 1.4 | 0.02em | Gray #6B7280 |
| Overline | Inter | 11px (0.6875rem) | 600 | 1.4 | 0.1em | Gold #C8A951 |
| Button | Inter | 14px (0.875rem) | 600 | 1 | 0.05em | (varies) |

### Mobile (Responsive Adjustments)

| Level | Desktop Size | Mobile Size | Notes |
|-------|-------------|-------------|-------|
| H1 | 48px | 32px (2rem) | Scale down significantly |
| H2 | 36px | 28px (1.75rem) | |
| H3 | 28px | 22px (1.375rem) | |
| H4 | 20px | 18px (1.125rem) | |
| Body | 16px | 16px | Do not reduce below 16px |
| Body Small | 14px | 14px | Minimum readable size |

---

## Spacing & Layout

### Line Length
- **Optimal:** 60-75 characters per line
- **Maximum:** 80 characters
- **Minimum:** 45 characters
- For wider layouts, use `max-width: 680px` on text containers

### Paragraph Spacing
- Space between paragraphs: 24px (1.5rem)
- Space after headings: 16px (1rem)
- Space before headings: 32px (2rem) — or 48px before H1/H2

### List Styling
- Use Inter Regular for list items
- Indent: 24px from left margin
- Vertical spacing between items: 8px
- Use navy (#1B2A4A) bullet points, not default black

---

## Capitalization

| Context | Style | Example |
|---------|-------|---------|
| Headlines (H1-H3) | Title Case | "Strategic Growth for Mid-Market Leaders" |
| Subheadings (H4-H5) | Title Case | "Our Approach to Market Analysis" |
| Body text | Sentence case | "We help companies identify new growth..." |
| Buttons | Title Case | "Get Started" / "Learn More" |
| Navigation | Title Case | "About Us" / "Our Services" |
| Overlines | ALL CAPS | "CASE STUDY" / "INSIGHTS" |

---

## Emphasis & Hierarchy

### Bold
Use Inter Medium (500) or Semibold (600) for emphasis within body text. Avoid using bold excessively — it loses impact when overused.

### Italic
Use sparingly. Acceptable for:
- Foreign words and technical terms on first use
- Book and publication titles
- Pull quote attributions

### Underline
Reserve underlines for hyperlinks only. Never underline for emphasis.

### Color as Emphasis
- Use Gold (#C8A951) for overlines and accent labels
- Use Navy (#1B2A4A) for key terms in body text (via font-weight change, not color alone)
- Never use color as the sole means of conveying information (accessibility)

---

## Print Typography

For printed materials (business cards, brochures, reports):

| Element | Font | Size | Weight |
|---------|------|------|--------|
| Document Title | Playfair Display | 24-36pt | Bold |
| Section Heading | Playfair Display | 18-24pt | Bold |
| Subheading | Inter | 12-14pt | Semibold |
| Body | Inter | 10-11pt | Regular |
| Caption | Inter | 8-9pt | Regular |
| Business Card Name | Playfair Display | 10pt | Bold |
| Business Card Details | Inter | 7.5-8pt | Regular |

---

## Implementation

### CSS Example
```css
/* Headlines */
h1, h2, h3 {
  font-family: "Playfair Display", Georgia, serif;
  color: #1B2A4A;
}

h1 {
  font-size: 3rem;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.02em;
}

/* Body */
body {
  font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 1rem;
  font-weight: 400;
  line-height: 1.6;
  color: #2C2C2C;
}

/* Overline accent */
.overline {
  font-family: "Inter", sans-serif;
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #C8A951;
}
```

### Tailwind Config
```javascript
fontFamily: {
  serif: ['"Playfair Display"', 'Georgia', 'serif'],
  sans: ['"Inter"', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
},
```
