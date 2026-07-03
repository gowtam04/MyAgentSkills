# Output Template

Write the strategy to `docs/design/fable-ui-strategy.md`, screenshots in
`docs/design/screens/`. The spine below is fixed — diagnosis → direction →
foundation → screens → sequence — because that order is the argument: each section
earns the next. Fill it with *this* app's specifics; a section that would read the
same for any app means you skipped the looking.

Keep it concrete and skimmable. Reference screenshots inline (`![Dashboard](screens/01-dashboard.png)`)
so every claim is next to the thing it's about. Prefer before→after phrasing and
real token values over adjectives.

---

```markdown
# UI Design Strategy — <App Name>

> Fable design pass · <date> · commit <short-sha>
> Seen via: <live screenshots | frontend source | user-provided screenshots>
> Status: **strategy only — no code changed.** Implementation is a separate pass.

## TL;DR

- **The diagnosis in one line:** <why it looks generic right now>
- **The direction:** <the taste thesis in one sentence, + reference products>
- **The three highest-impact moves:** <the 20% that delivers 80% of the lift>

## 1. Diagnosis — why it reads as generic today

### Systemic tells (repeat on every screen — fixed once, in the Foundation)
- <e.g. Default system font at a single 16px size — no type scale, so nothing
  reads as a title. (lens: typography)>
- <e.g. Neutrals are pure #888/#ccc — no ramp, which is what makes the palette
  feel cheap. (lens: color)>
- <one bullet per systemic tell, each naming its lens and pointing at evidence>

### Screen-specific problems (fixed per screen, in section 4)
- <Dashboard: nine equal-weight cards, no focal point. (lens: hierarchy)>

Be specific and evidenced. If a screen or aspect is genuinely fine, say so — this
section is honest, not a demolition.

## 2. Direction — what this app should feel like

<One or two sentences committing to a single direction and why it fits what the
app does and who uses it.>

**Reference points:** <2–3 real products that embody this direction, and what
specifically to borrow from each.>

Every recommendation below serves this direction.

## 3. Foundation — the cross-cutting system

The systemic tells above are all foundation gaps. Fixing these lifts every screen
before any screen-level work. Concrete values, not adjectives.

- **Typography** — typeface(s), the scale (list the steps), weights, and the
  role→size map (display / title / heading / body / caption).
- **Color** — the neutral ramp (list steps), accent(s), and semantic colors.
- **Space & rhythm** — the spacing scale and the grid.
- **Radius & elevation** — radius values and the elevation system (the levels and
  what each means).
- **Motion** — durations, easing curves, and the rule for what earns animation.

## 4. Screen-by-screen strategy

### <01 — Screen name>

![<screen>](screens/01-<screen>.png)

- **Current read:** <what it is; what specifically fails, referencing the shot>
- **Target:** <what it becomes under the direction + foundation>
- **Hero moment:** <the ONE focal element, made unmistakably dominant>
- **Concrete moves:**
  - <specific before→after change, tied to a foundation token>
  - <…>
- **Microinteractions & states:** <hover/press feedback; state transitions; the
  empty / loading / error states this screen needs>

### <02 — Screen name>
<…repeat per screen. A screen that's already good gets a short entry saying so.>

## 5. Priority & sequencing

- **Phase 1 — foundation + one signature moment (the 80/20):** <the handful of
  changes that deliver the dramatic lift; usually type scale + neutral ramp +
  spacing rhythm + one hero screen.>
- **Phase 2 — <theme>:** <…>
- **Phase 3 — polish & state coverage:** <…>

Ordered by impact, so the user can stop after any phase and still have gained.
```

---

## Chat summary (not in the file)

After writing the doc, in chat give: the one-line diagnosis, the direction and why,
the top 2–3 moves, and the path to the doc. Confirm `git status` shows only
`docs/design/` changed. If they want it built, note that's the next separate pass.
