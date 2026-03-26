# Bloom Typography Guide

## Font Stack

### Headings — Quicksand
- **Font:** Quicksand
- **Weights:** Bold (700) for H1-H2, Semibold (600) for H3-H4
- **Fallback:** `'Helvetica Neue', Arial, sans-serif`
- **Use for:** Page headings, hero text, marketing headlines
- **Source:** https://fonts.google.com/specimen/Quicksand

### Body — Lato
- **Font:** Lato
- **Weights:** Regular (400) for body text, Medium (500) for emphasis
- **Fallback:** `'Helvetica Neue', Arial, sans-serif`
- **Use for:** Body text, paragraphs, UI labels, descriptions
- **Source:** https://fonts.google.com/specimen/Lato

### Monospace — JetBrains Mono
- **Font:** JetBrains Mono
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
Quicksand and Lato form a harmonious pairing that reflects Bloom's brand personality of warmth and approachability. Quicksand's rounded, friendly letterforms evoke softness and calm, making it ideal for headings that welcome users into the wellness experience. Lato provides excellent readability at body text sizes with its semi-rounded details and sturdy structure, ensuring content is easy to consume during mindful reading. Both fonts share a humanist quality that aligns with Bloom's values of accessibility and genuine connection.

## Implementation

```css
@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600;700&family=Lato:wght@400;500&display=swap');

:root {
  --font-heading: 'Quicksand', 'Helvetica Neue', Arial, sans-serif;
  --font-body: 'Lato', 'Helvetica Neue', Arial, sans-serif;
  --font-mono: 'JetBrains Mono', 'Courier New', monospace;
}
```
