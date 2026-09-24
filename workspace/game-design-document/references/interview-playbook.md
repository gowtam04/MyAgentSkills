# Interview Playbook

How to extract a complete game design from someone who knows what they want but cannot yet say it.

## Mindset

- The user is the creative authority. You are the facilitator who forces specificity.
- Vague answers are unfinished design. Follow up once with concrete options or a scenario, not a lecture.
- Prefer **revealing tradeoffs** over open-ended essay questions.
- Recap often. People correct inaccurate recaps faster than they invent specs from scratch.
- Default to 1 focused `ask_user_question` per turn; batch up to 3 only when tightly related.
- Use `multi_select: true` for pillars, content types, platforms, juice priorities, cut lists.

## Pull Techniques

### 1. Reference-game calibration

Ask "more like A or B?" with two real games that isolate one axis.

Examples:

- Pace: *Dead Cells* (relentless) vs *Outer Wilds* (contemplative exploration)
- Failure: *Hades* (fail-forward meta) vs *Celeste* (instant retry skill)
- Combat: *Hollow Knight* (precise melee) vs *Enter the Gungeon* (bullet hell dodge)

Always follow with: "Where does *your* game diverge from that reference?"

### 2. First 60 seconds / first death / first win

Concrete timelines beat abstract genre labels.

- "Describe the first minute after New Game as if I'm watching over your shoulder."
- "What does the player's first failure look like, and what do they learn?"
- "What is the smallest victory that makes them want another run/level?"

### 3. Feel verbs before system names

Lead with player emotion, then reverse-engineer mechanics.

- Empowered, hunted, clever, cozy, tense, graceful, greedy, lost-on-purpose, masterful.
- "Which feeling is non-negotiable in the first vertical slice?"

### 4. Non-goals and anti-pillars

Ask what the game must **not** become.

- "What would make you abandon this project if it drifted that way?"
- Offer options: not a collectathon, not multiplayer, not story-heavy, not roguelike RNG, not grind MMO, etc.

### 5. Edge-case pressure

For each major system, ask one failure or conflict case.

- Two resources empty at once; player soft-lock; perfect play vs panic play; co-op desync fantasy; inventory full; missed tutorial.

### 6. Content counting

Never accept "lots of levels." Force counts or generation rules.

- "How many hand-authored levels for v1: 3 / 8 / 20+?"
- "Enemy roster size for slice vs ship?"
- "If procedural, what is authored vs generated?"

### 7. Cut-first list

Scope is design. Ask what dies first when time runs out.

- Order remaining features by "prove fantasy" vs "nice flavor."

### 8. Contradiction hunting

When answers conflict (cozy + hardcore permadeath; narrative-rich + endless arcade), surface the tension with two options that resolve it. Do not silently pick.

### 9. Prototype honesty

Ask what is already proven vs hoped.

- Label hoped mechanics as **design hypotheses** in the eventual docs.

## Option Quality Rules

- 2–4 options; realistic tradeoffs in descriptions.
- Put a recommended default first when context justifies it; mark "(Recommended)" only when earned.
- Do not pad with joke or obviously bad options.
- Include "hybrid / other" only when genuinely common; the UI already offers Other.
- Options should teach the user the design space (educative descriptions).

## Confirmation Pattern

After a major phase, prose recap then:

```
question: "Does this capture the design correctly so far?"
options:
  - Yes — continue
  - Mostly right — small fixes
  - Needs rework
```

## Phase Question Banks

Use as a menu, not a script. Skip what is already answered. Rephrase into option cards when a decision is needed.

### Phase 0 — Framing

- New game vs expansion vs single system?
- Solo / small team / client?
- Lean docs vs extensive package?
- Primary platform(s) and control method (mouse, gamepad, touch)?
- Target session length (2 min, 20 min, multi-hour)?
- Audience sophistication (kids, casual, midcore, hardcore, niche hobbyists)?

### Phase 1 — Vision And Pillars

- One-sentence pitch if explaining to a friend in an elevator.
- Player fantasy: role + activity ("a thief who never fights fair", "a gardener managing a dying starship").
- Top emotional beats during peak play.
- 3–5 pillars (multi-select from proposed set after free-text, then refine).
- Explicit non-goals.
- Closest comps and deliberate differences.
- "This game is succeeding when playtesters say ___."

### Phase 2 — Core Loop And Structure

- Atomic loop steps (explore → fight → loot → upgrade, etc.).
- What resets each death/run/level vs what persists.
- Camera and movement baseline (side-view, top-down, 3D third-person, etc.).
- Structure: linear levels, hub, open map, roguelike runs, matches, sandbox.
- How a session starts and ends.
- Victory conditions at micro and macro scale.

### Phase 3 — Systems

For each candidate system, resolve:

1. Why it exists (player experience goal).
2. Player inputs / verbs.
3. Resources and sinks.
4. Success and failure.
5. Feedback the player receives.
6. Interactions with other systems.
7. Slice priority: in-slice / post-slice / cut-candidate.

Systems often include some of: movement & traversal, combat, stealth, dialogue/choice, inventory, crafting, building, economy/shops, progression/XP, AI/enemies, bosses, multiplayer rules, base management, time systems, morality/reputation, vehicles.

Pressure questions:

- "What is the player doing with their hands every 2–5 seconds?"
- "What is the interesting decision, not just the action?"
- "What breaks if the player is very skilled? Very unskilled? Trying to break the game?"

### Phase 4 — Content And World

- Tone and setting in 3 adjectives + 1 reference.
- Narrative load: none / flavor only / quests / full story campaign.
- Cast size and relationship complexity if characters exist.
- World structure map in words (regions, levels, biomes).
- Content spreadsheet questions: counts for levels, enemies, items, weapons, abilities, NPCs, endings.
- Progression curve intent: gentle, steep, sawtooth, player-driven.
- Onboarding: tutorial mode, diegetic teaching, optional tips.

### Phase 5 — UX, Juice, Art, Audio

- Required screens (title, hub, HUD, inventory, map, settings, game over, credits).
- Information the HUD must always show vs on-demand.
- Juice priorities (multi-select): impact, clarity, comedy, horror unease, cozy warmth, spectacle.
- Art style anchors (pixel, flat vector, painterly, low-poly, collage, etc.) and silhouette priorities.
- Color / readability constraints.
- Music role: adaptive, loop beds, stingers-only, silence-forward.
- Voice acting: none / grunts / full VO.
- Accessibility must-haves.

### Phase 6 — Production Reality

- Deadline or target milestone (jam weekend, demo date, Early Access, none).
- Team skills that expand or limit design (no 3D artist, strong pixel artist, etc.).
- Engine/tool preferences as constraints only.
- Monetization if any (premium, free, cosmetics, none).
- Rating / content sensitivity targets.
- Vertical slice definition in one paragraph.
- Must-ship / stretch / cut-first ordered list.
- Top 3 design risks ("fun unproven", "scope", "tech", "narrative dependency").

## Soft Landing When The User Is Stuck

If they freeze:

1. Offer two complete micro-design directions for their pitch.
2. Ask which direction is closer.
3. Build the next questions on that direction.
4. Mark the other as an explicit non-path in Non-goals if rejected.

If they ramble:

1. Interrupt with a short recap of 3 bullets you heard.
2. Ask them to pick which bullet is the real core.
3. Park the rest under Stretch or Open Questions.

## Speed Mode

When the user asks to go fast:

- Prioritize Phases 1, 2, 3 (slice systems only), 6.
- Assume reasonable defaults for art/audio/UX; label them Assumptions.
- Write lean package unless they insisted on extensive.

## Thorough Mode (default)

- Cover all applicable phases.
- Force content counts and edge cases for every in-slice system.
- Do not write docs until Phase 7 confirmation passes (Yes or Mostly right with fixes applied).
