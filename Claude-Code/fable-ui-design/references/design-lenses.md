# Design Lenses

The lenses you diagnose through, and the principles that separate first-class from
generic. Read this before looking at a screen so you know what you're looking
*for*. When you critique, name which lens a problem lives in and point at the
specific element — that specificity is what keeps the strategy from reading like
the generic advice it's meant to replace.

## The core insight: "generic" is a systemic failure, not a missing shadow

When an app looks cheap, dry, or template-like, the cause is almost never "it
needs more polish." It's that the **foundation was never designed** — the app is
wearing its framework's defaults. Bootstrap's blue, Material's shadows, Tailwind's
untouched gray-500, the browser's 16px Times/Arial fallback. Defaults are
*neutral by construction* — built to be inoffensive on any app, which is exactly
why they read as generic on *this* one. The fastest route to first-class is
replacing defaults with decisions. Most of the lenses below are ways of spotting
where a default is still showing through.

## The eight lenses

### 1. Typography — the highest-leverage lens

Type is 90% of most interfaces, so it's where "generic" is won or lost. Look for:

- **No scale.** Everything is 14–16px with bold for "headings." First-class
  interfaces use a real modular scale (e.g. 1.25× steps: 12/14/16/20/25/31/39)
  so a title is unmistakably a title. Flat type = no hierarchy = the eye has no
  anchor.
- **Default system font doing all the work.** Not wrong, but untuned — no
  attention to weight, tracking, or line-height. A confident type choice (even a
  well-tuned system stack) instantly signals intent.
- **Line-height and measure ignored.** Body text at 1.2 line-height and full
  container width is a dead giveaway of "no one styled this." Comfortable reading
  is ~1.5 line-height and ~45–75 characters per line.
- **Too many sizes and weights.** The opposite failure — six sizes and four
  weights with no system. Restraint (a handful of roles, each mapped to one size)
  reads as considered.

### 2. Color

- **Missing neutral ramp.** The #1 cause of a "cheap" palette. Premium UIs run a
  wide, slightly-tinted gray ramp (10–12 steps) for text, borders, and surfaces;
  generic ones use pure `#000`/`#888`/`#ccc`/`#fff`. Getting the neutrals right
  matters more than the accent.
- **Default framework accent.** Bootstrap blue, Material indigo, Tailwind's
  default palette straight out of the box. A chosen accent — even one hue,
  disciplined — signals a brand.
- **Muddy or unlimited color.** Six competing accents, or colors picked ad hoc.
  First-class palettes are tight: a neutral ramp, one or two accents, and
  semantic colors (success/warn/error) that are tuned, not stock.
- **Contrast that's either weak (gray-on-gray, unreadable) or slamming (pure
  black on pure white, harsh).** Both read as unconsidered.

### 3. Space & rhythm

- **No spacing scale.** Margins and paddings are random numbers (13px here, 7px
  there). A scale (4/8/12/16/24/32/48…) makes density feel decided.
- **Cramped or evenly-timid.** Either everything is jammed together, or everything
  has the same medium gap so nothing groups. Space is how you show relationship —
  related things close, unrelated things apart. Generous whitespace around a focal
  element is one of the cheapest routes to "premium."
- **No grid / misalignment.** Elements that don't share edges. Alignment is free
  and its absence is immediately, if subconsciously, felt as sloppy.

### 4. Hierarchy & focal point

- **Everything the same weight.** The defining trait of generic screens: nine
  cards, all identical size and emphasis, so the eye bounces with nowhere to land.
- **No clear "first read."** On a first-class screen you know instantly what it's
  about. Ask of each screen: what is the ONE thing here? Then make it dominant
  (size, weight, color, space, position) and demote everything else. A screen
  without a focal point isn't designed, it's arranged.

### 5. Depth & elevation

- **Flat gray borders everywhere** (the un-designed look) **or** drop-shadows on
  everything (the trying-too-hard look). Both are the same mistake: elevation used
  as decoration instead of meaning.
- **Elevation should encode hierarchy** — what floats above what. A modal is above
  the page; a menu is above its trigger; a resting card is barely raised. Design a
  small elevation *system* (say 3–4 levels, soft and layered rather than one hard
  shadow) and use height to mean "closer to the user."
- Soft, multi-layer, low-opacity shadows read as expensive; single hard `0 2px
  4px rgba(0,0,0,0.5)` reads as a 2013 template.

### 6. Motion

- **None at all** — everything snaps, states change instantly, the app feels
  static and cheap.
- **Or gratuitous** — everything slides, bounces, and fades for no reason, which
  is its own generic tell (and slows the user down).
- First-class motion has a **grammar**: fast (150–250ms) for feedback, eased (not
  linear), and *earned*. It expresses one of four things — **feedback** (this
  responded to you), **causality** (this came from that), **continuity** (these
  two states are the same thing moving), or a rare, tasteful moment of **delight**.
  If a proposed animation expresses none of those, cut it.
- Microinteractions that matter most: hover/press feedback on interactive
  elements, smooth transitions between states (not hard cuts), and animated
  entrance for content that loads.

### 7. Consistency

- **The same thing styled differently in different places** — three button
  styles, two card treatments, inconsistent spacing between analogous screens.
  Inconsistency reads as amateur even when each instance is fine on its own.
- First-class = the same problem solved the same way everywhere. This is what a
  design system *is*, and it's why the foundation step pays off: decide once,
  apply everywhere.

### 8. State & content coverage

Cheap apps design only the happy path with placeholder data. The tells:

- **Empty states** that are a blank white void instead of a designed "nothing here
  yet, here's what to do."
- **Loading states** that are a raw spinner or a layout jump, instead of skeletons
  that hold the shape.
- **Error states** that are a red string of text.
- **Lorem ipsum / unrealistic data** — real content has varied lengths, long
  names, empty fields, huge numbers. Designing only for the tidy demo row is why
  real data later "breaks" the design.

Covering these states is one of the clearest lines between a demo and a product.

## What "first-class" actually means

So the recommendations don't drift back toward flashy-for-its-own-sake:

- **Restraint over decoration.** Premium design is usually *quieter* — fewer
  colors, fewer type sizes, more space, less motion. The instinct to add is
  usually wrong; the instinct to systematize and remove is usually right.
- **Consistency over novelty.** A boring pattern applied consistently beats a
  clever pattern applied unevenly.
- **Content-first.** The design serves real content and real tasks. Beauty that
  fights usability isn't first-class, it's a dribbble shot.
- **Details compound.** No single thing makes an app feel expensive; it's the
  accumulation of a hundred small decisions all pointing the same way — which is
  exactly why the *direction* (the taste thesis) matters more than any one fix.
