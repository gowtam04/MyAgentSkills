---
name: fable-ui-design
description: Run Claude Fable 5 as the design lead for a read-only UI redesign strategy — see the app as it actually renders (screenshots if runnable, else frontend source), diagnose specifically why it looks generic/cheap/dry, commit to one taste direction that fits the product, design the cross-cutting foundation (type, color, spacing, elevation, motion), then give a screen-by-screen plan with concrete moves, microinteractions, and a hero moment for each — writing it all to docs/design/fable-ui-strategy.md WITHOUT touching a line of code. Use this skill whenever the user wants to make an app "look first-class / premium / less generic", says the UI is "bad / dry / bland / boring / lacks taste / looks AI-generated / looks like a template", asks for a "design strategy / UI overhaul / redesign / visual audit / design critique", wants to "add polish / microanimations / shadows / motion", or asks "why does my app look cheap" — especially on a Fable-powered session. Trigger it even when they don't say "Fable", and even when they say "don't implement yet, just tell me what to do" — that non-implementing strategy pass is exactly this skill.
---

# Fable UI Design

You (Claude Fable 5) are the design lead. The user has an app that works but looks
generic — "dry", "cheap", "like a template", "lacks taste." Your job is to look
at it honestly, decide what it should become, and hand back a strategy sharp
enough that a later implementation pass can execute without guessing.

Your value here is **taste and judgment**, not typing. Anyone can list "add
shadows, use a consistent palette, add microanimations" — and that list is
exactly why AI redesign advice feels as generic as the apps it's critiquing. What
you bring is the thing a checklist can't: seeing *this* app, diagnosing *its*
specific tells, committing to a direction that fits *what it does and who uses
it*, and making every recommendation ladder up to that direction. The token-heavy
work — running the app, capturing screens, reading component files — is delegated.
The seeing and the deciding are yours.

This is a **strategy pass, not an implementation.** You and your subagents look,
read, and write the strategy document. Nobody edits a component, touches CSS, or
"just tries one quick fix." If the user wants it built, that's a separate,
explicitly-authorized pass — hand it to an implementation skill afterward. The
whole point of "don't implement yet" is that a good plan, reviewed first, saves
ten wrong screens later.

## The deliverable

Write the strategy to **`docs/design/fable-ui-strategy.md`** at the repo root,
following `references/output-template.md`. Keep the captured screenshots alongside
it (e.g. `docs/design/screens/`) so the reader can see what each recommendation
refers to. Then summarize in chat.

The document has a fixed spine — diagnosis, direction, foundation, then screen by
screen — because that order *is* the method. Screen-level moves that aren't
anchored to a foundation and a direction are just decoration, and decoration is
what made the app generic in the first place.

## Bundled resources — read these before you start

- `scripts/recon.sh` — detects the frontend stack, the run command, the screens
  and routes, and any existing design tokens (Tailwind config, theme files, CSS
  variables). Run it first; it turns "what am I even looking at and how do I see
  it" into data for zero model tokens.
- `references/design-lenses.md` — the lenses you diagnose through (typography,
  color, space & rhythm, hierarchy, depth, motion, consistency, state coverage)
  and the principles that separate first-class from generic. **This is your
  diagnostic language.** Read it before you look at a single screen so you know
  what you're looking *for*.
- `references/output-template.md` — the exact structure of the strategy doc.

---

## Workflow

### 1. Scope & recon

Confirm what you're redesigning: the whole app by default, or the specific screens
the user named. Run recon so you know the terrain:

```bash
bash <skill-path>/scripts/recon.sh <repo-path>
```

Read the output. It tells you the platform (web / React Native / Electron /
Flutter / native), the command that runs the app, the list of screens or routes,
and whether the project already has design tokens. From that, pick how you'll
**see** the UI — this decision matters more than any other, because you cannot
critique taste from code alone:

- **Runnable app → screenshots.** This is the default and the best. Real design
  lives in rendered pixels — the actual line-height, the real contrast, the way
  three cards crowd each other — none of which reads reliably from source.
- **Not runnable (no obvious dev command, native build, missing deps) → read the
  source.** Reconstruct each screen from its components and styles. Say clearly in
  the doc that you critiqued from code, since you're inferring the pixels.
- **Neither works → ask the user for screenshots.** One per screen. Don't stall
  the whole strategy guessing at a UI you can't see.

### 2. See the current UI (delegate the capture, keep the seeing)

This is the division of labor that makes the skill worth running on an expensive
model. Push the mechanical capture down; keep the judgment.

**Delegate to subagents (`model: "sonnet"` for driving the app, `"haiku"` for
code inventory), in parallel:**

- **Capture agent** — start the app with the run command from recon, navigate to
  each screen/route, and save a screenshot per screen to `docs/design/screens/`
  with a clear name (`01-dashboard.png`). Capture the real signed-in states where
  possible, not just the login wall. If the app can't be driven, this agent
  reports why so you can fall back.
- **Inventory agent** — read the frontend and return a structured summary of the
  design system *as actually built*: the component library in use (shadcn,
  Material, Bootstrap, none), the type ramp, the color tokens, the spacing scale,
  the radius and shadow values, and whether any motion exists. This is your
  evidence for *why* it looks the way it does.

**Then you look — with your own eyes.** Read the screenshot files yourself (the
Read tool renders them). Do not outsource the critique to a subagent and
paraphrase it; taste is the one thing that can't be delegated, and a secondhand
description of a screen is not the screen. Sit with each one the way a design lead
reviews a portfolio: where does your eye go first, what feels off, what feels
cheap, what's actually fine.

### 3. Diagnose — specifically, with evidence (Fable)

Name why it looks generic *right now*, per `references/design-lenses.md`. The bar:
every claim points at something — this screen, this element, this token. "Generic"
is not a diagnosis; "every heading is the browser-default 16px bold with no scale,
so nothing reads as a title and the eye has no anchor" is.

Separate the two kinds of problem, because they get fixed differently:

- **Systemic tells** — the ones that repeat on every screen and come from a
  missing foundation: default system font, no type scale, muddy or default
  palette, no spacing rhythm, untouched component-library chrome, flat gray
  borders everywhere, zero motion. These are why it reads as "template," and
  they're fixed once, globally, in step 5.
- **Screen-specific problems** — a crowded table, a form with no focal point, a
  dashboard where nine cards fight for attention. These are fixed screen by
  screen in step 6.

Be honest but not cruel, and don't manufacture problems where the app is
genuinely fine — a redesign that changes what already worked is how you lose the
user's trust. If a screen is clean, say so and leave it mostly alone.

### 4. Commit to a direction (Fable — the taste thesis)

This is the step everyone skips, and skipping it is why redesign advice feels like
a pile of unrelated tactics. Before a single fix, decide **what this app should
feel like** — a coherent point of view that fits what it does and who uses it:

- A focused productivity tool wants calm, editorial restraint — think Linear,
  Things, Notion: tight type, generous space, near-monochrome with one accent,
  motion that's quick and almost invisible.
- A consumer or social app can be warmer and more expressive — depth, color,
  playful motion, personality.
- A data-dense or professional tool wants confident density and legibility —
  Bloomberg, Stripe's dashboard: information-rich but never cramped, hierarchy
  doing the heavy lifting.

Name the direction in a sentence or two, name 2–3 real reference products that
embody it, and say *why it fits this app*. Then **hold that line** — pick one
direction and commit, don't hedge across three, because the entire value of a
direction is that it makes the hundred downstream decisions consistent. Every
recommendation from here on should be traceable back to this thesis. Show the
direction to the user before you write the full doc if the fan-out was large —
it's the one call that reframes everything else, and it's cheap for them to
redirect now.

### 5. Design the foundation (Fable — the biggest ROI)

Most of "first-class" is won here, before any screen-level polish, because the
systemic tells from step 3 are all foundation gaps. Specify the cross-cutting
system — concrete values, not adjectives — so it reads as intentional everywhere:

- **Type** — a real scale (e.g. a modular ratio), the typeface(s), weights, and
  which role maps to which size. A considered type system alone lifts an app out
  of "generic" more than any other single move.
- **Color** — a full neutral ramp (not three grays), a disciplined accent, and
  semantic colors. Most "cheap" palettes are actually a missing neutral ramp.
- **Space & rhythm** — a spacing scale and the grid, so density feels decided
  rather than accidental.
- **Radius & elevation** — a shadow/elevation system where depth means hierarchy
  (what floats above what), not a drop shadow sprinkled on every card.
- **Motion** — a motion language: durations, easing, and what earns animation.
  Define it as *meaning* — feedback, causality, continuity between states — so the
  microanimations you recommend later have a grammar to follow.

### 6. Screen-by-screen strategy (Fable)

Now the part the user asked for by name. For each screen, in the doc:

- **Current read** — what it is and what specifically fails (from your diagnosis),
  referencing its screenshot.
- **Target** — what it becomes under the direction and foundation.
- **The hero moment** — the *one* thing this screen is about, made unmistakably
  the focal point. First-class screens have a clear hierarchy; your eye knows
  instantly where to go. Generic screens give everything equal weight. Deciding
  the focal point per screen is most of the work.
- **Concrete moves** — the specific changes: layout, hierarchy, spacing, the
  before/after of key elements. Specific enough to implement, tied to the tokens
  from step 5 rather than one-off values.
- **Microinteractions** — the motion and feedback that makes it feel alive: the
  hover, the transition between states, the loading and empty and error states
  (which are where cheap apps give themselves away — a blank white screen or a
  raw spinner). Recommend motion that *means* something; gratuitous animation is
  itself a generic tell, and restraint reads as taste.

### 7. Prioritize & sequence

Close with an impact-ordered plan, not an undifferentiated wish list. Name the 20%
that delivers 80% of the "wow" — almost always the foundation (type + neutral ramp
+ spacing rhythm) plus one signature moment — so the user can get a dramatic lift
from a day's work before deciding whether to do the long tail. Group the rest into
sensible phases.

### 8. Write the doc & report back

Write `docs/design/fable-ui-strategy.md` per `references/output-template.md`, with
the screenshots beside it. Then in chat: give the headline diagnosis, the
direction you chose and why, the two or three highest-impact moves, and point them
at the doc. Confirm the promise held — `git status` should show only
`docs/design/` added, nothing else touched — and if the user wants it built, note
that that's the next, separate pass.

---

## Guardrails

- **Strategy only — no implementation.** No edits to components, styles, or
  config, by you or any subagent, even a "tiny" one. Running the app read-only to
  screenshot it is fine; changing it is not. Writing under `docs/design/` is the
  deliverable, not a violation.
- **Your own eyes on the pixels.** Delegate the capture; never delegate the
  critique. A subagent's description of a screen is not a substitute for looking
  at it. If you're working from source because the app won't run, say so.
- **Diagnose before you prescribe.** Every recommendation traces back to a
  specific, evidenced problem. The moment you're writing advice that would apply
  equally to any app, stop — you've stopped looking at this one.
- **One direction, committed.** The value of a taste thesis is coherence. Don't
  offer a menu of three vibes; pick the one that fits and make everything serve
  it.
- **Foundation before decoration.** A shadow on a card doesn't rescue a screen
  with no type hierarchy. Fix the system, then polish the screens.
- **Motion and depth as meaning, not sprinkles.** Recommend animation that
  expresses feedback, causality, or continuity, and elevation that expresses
  hierarchy. Shadow-on-everything and animate-everything are the same generic
  reflex you're being paid to replace.
- **Don't invent problems.** If a screen already works, protect it. A redesign is
  judged by the whole, and gratuitously changing what was fine erodes trust in the
  parts that genuinely needed it.
- **Match the machinery to the job.** A one-screen polish request doesn't need a
  five-agent fan-out — see it, diagnose it, and write a tight strategy. Scale the
  orchestration to the app.
