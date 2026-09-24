# Templates

Fill every applicable section with project-specific content. Delete sections that truly do not apply; do not leave "N/A" walls. Prefer bullets and tables.

Status tags used across files: `hypothesis` | `prototyped` | `locked`.

---

## README.md

```markdown
# {Game Title} — GDD Index

**Status:** {draft | active | slice-frozen}
**Last updated:** {YYYY-MM-DD}
**Package shape:** {lean | standard | feature}

## How To Use This GDD

- Start at [00-one-pager](./00-one-pager.md) for orientation.
- Treat playable builds as truth when they conflict with text; then update the text.
- System rules live only under systems docs — do not fork copies into tickets without linking back.

## Documents

| Doc | Purpose |
|---|---|
| [00-one-pager](./00-one-pager.md) | North star |
| ... | ... |

## Notable Decisions

| Date | Decision | Why |
|---|---|---|
| | | |

## Owners

| Area | Owner (if known) |
|---|---|
| Design lead | |
```

---

## 00-one-pager.md

```markdown
# {Game Title} — One-Pager

## Logline
{One sentence: who you are, what you do, what makes it distinct.}

## Elevator Pitch
{2–4 sentences. Fantasy + core activity + hook.}

## Design Pillars
1. **{Pillar}** — {what it means in play}
2. ...

## Non-Goals
- {What this game is deliberately not}

## Core Loop
{Atomic steps, e.g. Explore → Risk → Reward → Upgrade → Repeat}
- **Second-to-second:** ...
- **Minute-to-minute:** ...
- **Session / meta:** ...

## Player Fantasy And Feel
- **You are:** ...
- **You feel:** ...
- **Peak moment:** ...

## Comps (Calibration Only)
| Reference | Take | Leave |
|---|---|---|
| {Game} | | |

## Vertical Slice
{One paragraph: the smallest playable that proves the fantasy.}

## Platforms And Session
- **Platforms:** ...
- **Session length:** ...
- **Controls:** ...

## Scope Snapshot
- **Must-ship:** ...
- **Stretch:** ...
- **Cut first:** ...

## Deep Links
- Vision → `01-vision-and-pillars.md`
- Loop → `02-core-loop-and-structure.md`
- Systems → `03-systems.md`
- Production → `07-production-and-slice.md`
```

---

## 01-vision-and-pillars.md

```markdown
# Vision And Pillars

## Vision Statement
{What the game is, why it is interesting, what is unique.}

## Target Player
- **Who:** ...
- **What they want from games like this:** ...
- **What they should say after 20 minutes:** ...

## Player Fantasy
{Role, power fantasy or anti-power fantasy, emotional promise.}

## Design Pillars
For each pillar:
### {Pillar name}
- **Means in play:** ...
- **Supports systems:** ...
- **Violations look like:** ... (how we know we drifted)

## Non-Goals / Anti-Pillars
| Non-goal | Why excluded |
|---|---|
| | |

## Success Criteria
- **Playtest signals:** ...
- **Personal/project goals:** {art, commercial, learning, portfolio, etc.}

## Comparable Titles
| Title | Similarity | Divergence for this game |
|---|---|---|
| | | |

## Tone And Theme
{Keywords + short paragraph. Keep story detail in 04 if heavy.}
```

---

## 02-core-loop-and-structure.md

```markdown
# Core Loop And Structure

## Camera And Perspective
{e.g. side-view 2D, top-down, 3D third-person...}

## Control Baseline
| Action | Input (provisional) | Notes |
|---|---|---|
| Move | | |
| Primary | | |
| ... | | |

## Loops

### Second-to-second
{What hands and eyes do continuously.}

### Minute-to-minute
{Decisions and reward rhythm.}

### Session / meta
{What persists between deaths, levels, days, runs.}

## Game Structure
- **Structure type:** {linear levels | hub | open | roguelike runs | matches | sandbox | ...}
- **Progression of spaces:** ...
- **How content is gated:** ...

## Win, Loss, And Recovery
- **Micro success:** ...
- **Micro failure:** ...
- **Run/level failure:** ...
- **Meta progress on failure:** {none | currency | unlocks | knowledge | ...}

## First 60 Seconds
{Beat-by-beat new game experience.}

## First 10 Minutes
{What systems unlock, what mastery begins.}

## Pacing Intent
{Tension curve, rest beats, difficulty spikes — high level.}
```

---

## 03-systems.md

```markdown
# Systems

## System Map
| System | Pillars served | Loop step | Status | In slice? |
|---|---|---|---|---|
| | | | hypothesis/prototyped/locked | Y/N |

## Dependencies
{Bullet graph: Combat → Stamina → Movement; Economy → Upgrades → Combat; etc.}

## Systems
{For each system, use the System entry block below.}
```

### System entry (also used for `systems/*.md`)

```markdown
### {System name}
- **Status:** hypothesis | prototyped | locked
- **In vertical slice:** yes | no
- **Player experience goal:** {why this exists; the feeling}
- **Pillars served:** ...

#### Verbs
| Player verb | Game response | Constraints |
|---|---|---|
| | | |

#### Resources And Rules
- **Resources:** ...
- **Costs / cooldowns / limits:** ...
- **Success conditions:** ...
- **Failure conditions:** ...
- **Edge cases:** ...

#### Numbers
| Parameter | Value or range | Status |
|---|---|---|
| | | TBD-tunable / locked |

#### Feedback
{What the player sees/hears/feels on success, fail, and near-miss.}

#### Interfaces To Other Systems
| Other system | Input from / output to |
|---|---|
| | |

#### Content It Consumes
{Enemy types, item categories, level tags — counts live in 04.}

#### Open Risks
{Unproven fun bets specific to this system.}
```

---

## 04-content-and-world.md

```markdown
# Content And World

## Setting
{Place, time, premise. Short.}

## Narrative Load
**Level:** none | flavor only | quests | full campaign

### Story Overview
{Only if narrative load > flavor. Synopsis, not a novel.}

### Story Beats / Acts
| Beat | Player experience | Unlocks / changes |
|---|---|---|
| | | |

### Characters
| Character | Role in play | Relationship | Notes |
|---|---|---|---|
| | | | |

## World Structure
{Regions, levels, biomes, hubs — how they connect.}

## Content Inventory (v1)
Be explicit. Prefer integers. For procedural content, state authored seeds vs generated rules.

| Content type | Slice count | Ship count | Notes |
|---|---|---|---|
| Levels / biomes | | | |
| Enemy types | | | |
| Bosses | | | |
| Weapons / abilities | | | |
| Items | | | |
| NPCs / quests | | | |
| ... | | | |

## Progression And Unlocks
- **What grows:** power / knowledge / map access / build options / ...
- **Unlock schedule intent:** ...
- **Soft vs hard gates:** ...

## Difficulty And Onboarding
- **Challenge philosophy:** ...
- **Assists / modes:** ...
- **How complexity is taught:** ...
```

---

## 05-ux-ui.md

```markdown
# UX And UI

## Screen List
| Screen | Purpose | Entry / exit |
|---|---|---|
| Title | | |
| Gameplay HUD | | |
| Pause / settings | | |
| Inventory / map | | |
| Results / game over | | |
| ... | | |

## Flow
{Describe primary navigation as a short list or mermaid-friendly steps.}

## HUD
| Element | Always visible? | Priority | Notes |
|---|---|---|---|
| Health | | | |
| ... | | | |

## Controls (detail)
| Action | KBM | Gamepad | Touch | Remappable? |
|---|---|---|---|---|
| | | | | |

## Menus And Meta UX
{Settings expected: audio, graphics, accessibility, language, credits.}

## Feedback And Clarity
- **Critical info that must never be missed:** ...
- **Tutorials / coach marks policy:** ...

## Accessibility
| Requirement | Priority | Notes |
|---|---|---|
| Full remapping | | |
| Colorblind-safe palette | | |
| Subtitles | | |
| Difficulty assists | | |
| UI scale | | |
```

---

## 06-art-audio-juice.md

```markdown
# Art, Audio, And Juice

## Art Direction
- **Style:** ...
- **References (calibration):** ...
- **Silhouette / readability priorities:** ...
- **Palette intent:** ...
- **Camera / presentation notes:** ...

## Animation Priorities
{What must read clearly: run cycle, attack windup, hurt, death, interact, UI transitions.}

## Juice / Game Feel
| Moment | Desired feel | Feedback tools (SFX, VFX, hitstop, shake, haptics) |
|---|---|---|
| Hit confirm | | |
| Perfect action | | |
| Failure | | |
| Reward | | |

## Audio Direction
- **Music role:** ...
- **SFX priorities:** ...
- **Voice:** none | grunts | full VO
- **Reference tracks / tones:** ...

## Asset Lists (planning counts)
| Asset category | Slice | Ship | Notes |
|---|---|---|---|
| Player sprites/models + anims | | | |
| Enemy set | | | |
| Tiles / props | | | |
| UI icons / frames | | | |
| VFX | | | |
| Music tracks | | | |
| SFX | | | |
```

---

## 07-production-and-slice.md

```markdown
# Production And Vertical Slice

## Constraints
- **Team:** ...
- **Timebox:** ...
- **Engine / tools preferences:** {constraints only}
- **Platform certification / rating notes:** ...
- **Business model:** {premium | free | N/A | ...}

## Vertical Slice Definition
**Goal:** prove {fantasy / pillars X,Y}.

### In Slice
- Systems: ...
- Content: ...
- UX: ...
- Art/audio bar: {greybox | keyed style | polished}

### Out Of Slice (but in ship vision)
- ...

### Explicitly Cut / Not Planned
- ...

## Scope Lists
| Item | Must-ship | Stretch | Cut first (order) |
|---|---|---|---|
| | | | |

## Milestones (if known)
| Milestone | Exit criteria |
|---|---|
| Greybox slice | |
| Styled slice | |
| Content complete | |
| Polish / ship | |

## Risks
| Risk | Why it matters | Mitigation |
|---|---|---|
| Fun unproven in X | | Prototype early |
| Scope creep in Y | | Cut-first order |
| Dependency on Z | | |

## Levels Of Quality (optional, for larger projects)
| Level | Meaning | Example for core feature |
|---|---|---|
| L0 | Playable stub | |
| L1 | Main mechanics + rough UI | |
| L2 | Feature-complete for design | |
| L3 | Integrated SFX/VFX/narrative hooks | |
| L4 | Ship polish | |
```

---

## 08-open-questions.md

```markdown
# Open Questions

Only unresolved items. Remove questions when decided; move the decision into the owning doc.

| ID | Question | Blocking? | Options under consideration | Owner |
|---|---|---|---|---|
| Q1 | | Y/N | | |

## Parking Lot
Ideas not in scope for v1 but worth remembering:
- ...
```

---

## Lean single-file option (`gdd.md`)

Use only for tiny projects. Order:

1. One-pager sections  
2. Systems (all system entries)  
3. Content inventory table  
4. Slice + cuts + risks  
5. Open questions  

---

## Feature package (`features/{name}/design.md`)

```markdown
# Feature: {Name}

## Intent
- **Player experience goal:** ...
- **Pillars served:** ... (link parent GDD)
- **Loop step:** ...

## Design
{System entry fields: verbs, rules, numbers, feedback, edges, interfaces}

## UX
{Screens, HUD changes, flows}

## Content
{Counts and dependencies}

## Acceptance (playtestable)
- [ ] ...
- [ ] ...

## Slice / Status
- **Status:** hypothesis | prototyped | locked
- **In next milestone:** yes | no
```
