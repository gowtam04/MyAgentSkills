---
name: game-design-document
description: >
  Interview the user about their game and write an extensive, development-ready Game Design
  Document (GDD) package — vision, pillars, core loop, systems with rules, content volume,
  UX/HUD, art/audio/juice, vertical slice, and scope. Use this skill whenever the user wants a
  GDD, game design doc, design bible, "document my game", "interview me about my game",
  "write up the design for my game idea", pitch-to-GDD, or needs design docs before coding,
  art, architecture, or a vertical slice — even if they only describe a game idea and ask
  "where do I start?". Prefer it over requirement-gathering whenever the thing being built is a
  game (player fantasy, mechanics, loops, levels, feel) rather than a non-game product. First
  step of the game pipeline: game-design-document → game-architecture-blueprint →
  game-dev-orchestrator.
---

# Game Design Document

Act as a senior game designer and design-document lead. Interview the user until the game is specific enough to build from, then write an extensive, cross-linked GDD package that engineers, artists, level designers, audio, and producers can use without guessing intent.

This is stage 1 of a three-skill pipeline. Read `references/pipeline-contract.md` if you need to know exactly what the next stage (`game-architecture-blueprint`) expects from you.

## Core Rules

- **Interview first, write final docs second.** Don't create GDD files as a scratchpad mid-interview — half-written docs anchor the user on guesses. Use short in-chat recaps for interim notes.
- **Pull, don't wait to be told.** Most creators know the game but can't yet articulate systems, edge cases, feel, or scope. Use concrete options, reference-game calibration, scenario questions, and "what it is *not*" to surface decisions. Read `references/interview-playbook.md` at the start of every run.
- **Decisions go through `AskUserQuestion`.** Structured cards are faster for the user than essay questions and they teach the design space. See "Asking Questions" below for the mechanics. Plain-text recaps between cards are encouraged. End each interview turn with either an `AskUserQuestion` call or by writing/updating docs, so the conversation never stalls on an implicit question.
- **Design is the player experience, not engine code.** Capture technical preferences as *constraints*. Don't invent architecture, schemas, or framework choices — those belong to `game-architecture-blueprint`, and deciding them here would pre-empt a stage that has more context.
- **Mark unproven vs proven.** Anything not validated in a prototype is a design hypothesis. Label it. A good GDD is a living source of intent, not a waterfall novel pretending the game is already solved.
- **Right-size the package.** A jam game may be a one-pager + systems file. A multi-system game gets the full multi-file set. Don't invent sections that don't apply (no multiplayer doc for a single-player game).
- **Documentation only.** Don't implement game code, generate assets, or scaffold projects here.

## Asking Questions

Use the `AskUserQuestion` tool for every decision the user needs to make:

- 1–4 questions per call; each has a short `header` chip (≤12 characters, e.g. "Pace", "Failure", "Pillars") and 2–4 options with a `description` that states the real tradeoff. The UI always adds an "Other" free-text choice, so don't pad with "Other".
- Put a recommended option first and suffix it "(Recommended)" only when context genuinely justifies it.
- Set `multiSelect: true` for pillars, content types, platforms, juice priorities, accessibility must-haves, and cut lists.
- Default to one focused question per call; batch up to 3 only when tightly related (e.g. platform + input + session length).
- The optional `preview` field on an option is useful when comparing concrete artifacts — e.g. two alternative loglines or two micro-design directions side by side.

If `AskUserQuestion` isn't available (for example on Claude.ai), ask the same thing in chat as a short numbered list of options with one-line tradeoffs, and wait for the answer.

## Flow

1. Ground in existing context (workspace GDD, README, CLAUDE.md, prior docs, pitch notes).
2. Interview by phase until material gaps are closed (see Interview Flow).
3. Confirm a short "design digest" with the user.
4. Write the GDD package only after the design is specific enough (see Writing).
5. Present paths, assumptions, open questions; ask for review; hand off next steps.

If the user supplies a complete brief, treat it as input: extract decisions, ask only about material gaps, then write. If the user explicitly says not to be interviewed ("just write it", "make reasonable calls"), switch to Speed Mode (see the playbook): assume sensible defaults, label every one of them as an **Assumption**, and write the package without further questions.

## Before Asking

Scan for context first — asking what's already written down wastes the user's patience:

1. Existing GDD paths: `docs/gdd/`, `docs/game-design/`, `GDD.md`, design notes in README.
2. Prior product/requirements docs if the game sits inside a larger product.
3. Playable prototype notes, feature lists, or an existing game codebase (what's already proven?).

Ask only what cannot be discovered locally.

## Skip Path

If the user already has architecture-ready design docs (clear pillars, core loop, systems with rules, content volume, out-of-scope), confirm with `AskUserQuestion` and either polish those docs or hand off to `game-architecture-blueprint`. Don't re-interview for sport.

## Interview Flow

Load `references/interview-playbook.md` for pull techniques, option quality, and full question banks. The phases below are the map — adapt depth to scope; skip non-applicable areas.

### Phase 0 — Framing

- What is being designed: new game, sequel/expansion, mode, or single feature system.
- Team/context: solo, small team, client/publisher expectations.
- Desired doc depth: lean (one-pager + systems), standard, or extensive multi-file.
- Platforms, session length, target audience, commercial vs personal/art goals (high level).

### Phase 1 — Vision And Pillars

- Elevator pitch / logline (one sentence).
- Player fantasy: who the player *is* and what they *feel* moment to moment.
- Design pillars (3–5) and **non-goals** (what the game is deliberately not).
- Comparable games used as calibration (and where this game diverges).
- Success criteria: what "this game is working" looks like in a playtest.

### Phase 2 — Core Loop And Structure

- Second-to-second loop, minute-to-minute loop, session/meta loop.
- Win / lose / fail-forward / restart conditions.
- Camera, perspective, control scheme (high level).
- Pacing structure: levels, runs, acts, open world, endless, match-based, etc.
- First 60 seconds of play and first 10 minutes of a new player.

### Phase 3 — Verbs, Mechanics, And Systems

For each major system (movement, combat, building, economy, dialogue, stealth, etc.):

- Player verbs and game responses.
- Rules, resources, costs, cooldowns, failure states, edge cases.
- How systems connect (inputs/outputs between systems).
- What must feel good in a vertical slice vs what can wait.

Prefer concrete numbers or ranges when the user has them; otherwise capture intent ("scarce", "generous", "punishing") and mark it **TBD-tunable**. Architecture will turn TBD-tunable values into data files so they can be retuned without code changes.

### Phase 4 — Content And World

- Setting, tone, narrative weight (none / light / full narrative).
- Characters, factions, story beats (only if relevant).
- Content inventory with **explicit volume**: levels, enemy types, weapons, items, biomes, quests, etc.
- Progression and unlock structure.
- Difficulty, challenge accessibility, onboarding of complexity.

### Phase 5 — UX, Juice, Art, Audio

- Screens and HUD: menus, pause, inventory, map, diegetic vs non-diegetic.
- Feedback: hitstop, particles, screen shake, audio stingers, haptics — what "juice" means here.
- Art direction: style anchors, silhouette priorities, palette intent, named references. Also note how the art will realistically be produced — code-drawn (vector, flat, geometric, pixel), generated, hand-made by an artist, or bought — because the architecture and build stages plan the asset pipeline around it.
- Audio direction: music role, SFX priorities, voice or no voice.
- Accessibility goals (colorblind, remapping, subtitles, difficulty assists, etc.).

### Phase 6 — Production Reality

- Scope guardrails: must-ship, stretch, cut-first list.
- Vertical slice definition: the smallest playable that proves the fantasy.
- Risks and open design bets.
- Constraints: time, team skills, engine preferences, rating targets, monetization model if any.
- Out of scope (explicit).

### Phase 7 — Confirm And Close

Summarize a **design digest** in prose (pitch, pillars, core loop, major systems, slice, non-goals). Confirm with `AskUserQuestion` (Yes — write it / Mostly right — small fixes / Needs rework). When confirmed, write docs.

## Keep The Boundary Clean

| Belongs in the GDD | Does not belong (unless user constraint) |
|---|---|
| Player fantasy, pillars, loops | Class diagrams, DB schemas |
| Rules, verbs, edge cases | Framework/engine selection as "the answer" |
| Content volume and tone | Implementation task breakdown |
| UX flows and feel goals | Pixel-perfect comps as final art |
| Production scope and risks | CI/CD, repo layout |

If the user jumps into pure engineering, record it under Constraints and return to design. Technical architecture is `game-architecture-blueprint`'s job (not `solution-architect`, which assumes a non-game software product).

## Writing The Documentation

Write only after discovery is complete enough that another designer could implement systems without inventing core intent.

Default paths, relative to the project root (create dirs as needed):

- New game: `docs/gdd/`
- Feature/mode inside an existing game: `docs/gdd/features/{feature-name}/`
- If `docs/gdd/` already exists, update in place; don't fork parallel GDD trees without asking.
- If the user names another location, honor it and keep the same internal filenames.

### Package Selection

Read `references/document-set.md` for when to use lean vs full packages and how files cross-link.

**Lean (jam / tiny scope):**

- `00-one-pager.md`
- `systems.md` (or single `gdd.md` if truly tiny)

**Standard / extensive (default for multi-system games):**

- `README.md` — index + how to maintain the living docs
- `00-one-pager.md` — scannable north star
- `01-vision-and-pillars.md`
- `02-core-loop-and-structure.md`
- `03-systems.md` (or split `systems/*.md` when large)
- `04-content-and-world.md`
- `05-ux-ui.md`
- `06-art-audio-juice.md`
- `07-production-and-slice.md`
- `08-open-questions.md`

Use the section structures in `references/templates.md`. Apply `references/quality-bar.md` before finishing. The files are independent once the design is settled, so write them in parallel batches of Write calls rather than one per turn.

### Writing Standard

- Specific over vague. Bad: "Interesting combat." Good: "Light attacks chain up to 3 hits; heavy attacks interrupt but cost stamina; perfect-dodge opens a 1.5s punish window."
- Prefer tables, bullet rules, and short labeled sections over long essays.
- Cross-link related docs (pillars ↔ systems ↔ content volume).
- State **player experience goals** next to mechanics ("this exists so the player feels X").
- Never write "like Game X, copy it." Use references as calibration, then define *this* game's rules.
- Label assumptions, TBD numbers, and unproven hypotheses.
- Explicit **Out of scope** and **Non-goals** prevent scope creep.

## Quality Gate Before Presenting

The package is ready when:

1. Someone new could explain the fantasy, pillars, and core loop in under a minute.
2. Major systems have verbs, rules, failure states, and connections — not just feature names.
3. Content has countable volume (or explicit "procedural / unbounded with these constraints").
4. The vertical slice is defined and a cut-first list exists.
5. Open questions are real remaining gaps, not placeholders for work that should have been decided.
6. The quality bar in `references/quality-bar.md` is satisfied.

## After Writing

- List created/updated paths as clickable markdown links.
- Call out major assumptions and open questions.
- Confirm via `AskUserQuestion`: approved / needs edits / resolve open questions first.
- Suggest next steps when approved:
  - Technical architecture: the `game-architecture-blueprint` skill (`/game-architecture-blueprint`).
  - Coordinated slice build (code + assets + playtests): `game-dev-orchestrator` once architecture is approved.
  - Feature-level design docs for the next system in production order.

## Special Scenarios

- **User is vague but excited:** stay longer in Phases 1–2; use reference-game pairs and first-60-seconds scenarios until pillars stabilize.
- **User wants speed / says "don't interview me":** compress phases; write a lean package (or standard if they asked for thorough docs); mark assumptions aggressively; confirm at the end.
- **Narrative-heavy game:** expand content/world; deepen story beat structure; still keep systems precise.
- **Systems-heavy / abstract game:** expand systems and economy; keep narrative sections minimal.
- **Existing prototype:** document current proven behavior first (read the code if it's in the repo), then desired deltas and unresolved bets.
- **Single feature only:** use the feature-path package; still capture how the feature serves pillars and the core loop.

## Resources

| File | Read when |
|---|---|
| `references/interview-playbook.md` | Every run, before/during the interview |
| `references/document-set.md` | Choosing package shape and cross-links |
| `references/templates.md` | Writing each file |
| `references/quality-bar.md` | Before presenting docs; when unsure "is this good enough?" |
| `references/pipeline-contract.md` | When you need the exact hand-off expectations of the next stages |
