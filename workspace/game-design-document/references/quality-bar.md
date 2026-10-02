# Quality Bar

Research-backed standards for a GDD that teams actually use. Apply before presenting docs.

## What A Good GDD Is

A good game design document turns a game idea into an **actionable plan** others can build from: vision, rules, content volume, feel, and scope guardrails. It is a **living, searchable source of intent**, not a waterfall novel written once and abandoned.

Modern practice favors:

1. **Vision first** — logline, pillars, non-goals, player experience goals.
2. **Core loop clarity** — second-to-second and session loops before feature laundry lists.
3. **Master + detail** — a scannable one-pager plus deeper system/content docs (not one unreadable monolith).
4. **Specificity** — verbs, rules, edge cases, and countable content; not "interesting combat."
5. **Why + what** — every major system states the feeling it serves.
6. **Cross-discipline usefulness** — design, eng, art, audio, UX, production can each find their section.
7. **Scope honesty** — slice definition, cut-first list, explicit out-of-scope.
8. **Prototype humility** — unproven ideas labeled; playable builds eventually outrank stale text.
9. **Findability** — headings, tables, cross-links; written for scanning.
10. **Project-shaped** — omit sections that do not apply; never checkbox-fill empty ceremony.

## Pass / Fail Checklist

### Vision

| Check | Pass looks like |
|---|---|
| Logline | One sentence a stranger understands |
| Pillars | 3–5; each has "means in play" and "drift looks like" |
| Non-goals | At least a few explicit exclusions |
| Fantasy | Role + feeling, not only genre label |

### Loop And Structure

| Check | Pass looks like |
|---|---|
| Atomic loop | Ordered steps, not a feature list |
| Failure / recovery | What happens on death/loss is defined |
| First 60 seconds | Beat-level, not "tutorial then play" |
| Structure | Levels/runs/hub/open stated clearly |

### Systems

| Check | Pass looks like |
|---|---|
| Verbs | Player actions named; game responses named |
| Rules | Resources, limits, success/fail, edge cases |
| Connections | Systems declare inputs/outputs to others |
| No clone-by-name | References calibrate; rules are *this* game's |
| Status | Hypothesis vs prototyped vs locked |

### Content

| Check | Pass looks like |
|---|---|
| Counts | Integers or generation rules for major content types |
| Progression | What unlocks and how gated |
| Narrative right-sized | Depth matches stated narrative load |

### UX / Presentation

| Check | Pass looks like |
|---|---|
| Screens | Listed with purpose |
| HUD | Critical info prioritized |
| Juice | Key moments have intended feedback |
| Accessibility | At least priority targets if shipping to players |

### Production

| Check | Pass looks like |
|---|---|
| Vertical slice | Proves named pillars/fantasy with listed systems/content |
| Cut-first | Ordered sacrifices under time pressure |
| Risks | Top design/production risks with mitigations |
| Constraints | Time, team, platform, preferences recorded as constraints |

### Document Craft

| Check | Pass looks like |
|---|---|
| Scannable | Short sections, tables, bullets dominate |
| Single home | Facts not restated in conflicting full form |
| Open questions | Real gaps only; not a dumping ground for laziness |
| Assumptions | Marked where the interviewer filled a hole |

## Anti-Patterns (reject or rewrite)

- **The unread novel** — tens of pages of prose with no one-pager or index.
- **Feature laundry list** — systems named without verbs, rules, or failure.
- **"Like Game X"** as specification — references without this game's rules.
- **False confidence** — detailed untested combat math presented as locked truth.
- **Scope fog** — "lots of content" with no counts or generation constraints.
- **Ceremony sections** — empty Marketing/Monetization/Tech chapters written to fill a template.
- **Engine cosplay** — class hierarchies and package structure masquerading as design.
- **Pillars as adjectives** — "fun, immersive, unique" with no playtestable meaning.
- **Orphan systems** — mechanics that do not serve a pillar or loop step.
- **Stale dual truths** — docs contradict the prototype with no changelog or update.

## Bad → Good Examples

**Bad:** "Combat is fast and satisfying."

**Good:** "Light attacks chain to a 3-hit combo (0.25s / 0.25s / 0.4s). Heavy attack has 0.5s windup, interrupts lights, costs 25 stamina. Dodging during an enemy's red flash triggers a 1.5s riposte window. Goal: the player feels sharp and brave, not button-mashy."

**Bad:** "There are many levels and enemies."

**Good:** "Slice: 1 tutorial space + 2 combat arenas + 1 mini-boss. Ship v1: 8 hand-authored levels across 3 biomes; 6 enemy types + 2 bosses. No procedural level gen in v1."

**Bad:** "UI will be intuitive."

**Good:** "Gameplay HUD always shows HP, stamina, and current objective. Inventory is a pause grid (5×4). Critical hits use a distinct SFX + white flash; low HP pulses the HP pip red."

**Bad:** "Inspired by Stardew and Dark Souls."

**Good:** "Cozy farm meta like Stardew (low-pressure day planning) + rare high-stakes delves with Souls-like telegraph reading. Non-goal: Souls-like punishment on the farm layer; farm progress never permadeletes."

## Right-Sizing

| Project | Expected package | Interview depth |
|---|---|---|
| Weekend jam | One-pager + systems | Phases 1–3, 6 compressed |
| Solo MVP | Standard set, thinner narrative/audio if unused | All applicable phases |
| Multi-system / team | Full standard + systems split as needed | Thorough mode |
| Single feature | Feature package linked to parent GDD | Feature-focused + pillar fit |

Longer is not better. **Clearer and more specific** is better. If a section does not change a build decision, cut it.

## Final Gate (must all be true)

1. A new teammate can restate fantasy, pillars, and core loop in under a minute after reading the one-pager.
2. Every in-slice system has verbs, rules, and failure — not just a name.
3. Content volume is countable or procedurally constrained.
4. Vertical slice and cut-first list exist.
5. Open questions are only true unknowns.
6. No anti-pattern above remains unaddressed without an explicit reason.
