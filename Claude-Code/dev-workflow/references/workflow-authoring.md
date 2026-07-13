# Authoring the build workflow

The copy-adaptable JavaScript template for the build workflow. Read this before writing the script
(Step 3/4). Adapt it to this project's phases — don't write orchestration from scratch.

## Contents
- [How the pieces map to the TDD cycle](#how-the-pieces-map-to-the-tdd-cycle)
- [Authoring rules that keep the script correct](#authoring-rules-that-keep-the-script-correct)
- [The template](#the-template)
- [Adversarial review with refutation voting](#adversarial-review-with-refutation-voting)
- [Worktree isolation (only when agents collide)](#worktree-isolation-only-when-agents-collide)
- [Parameterizing with args, rerun, and resume](#parameterizing-with-args-rerun-and-resume)

## How the pieces map to the TDD cycle

| TDD step                        | Workflow encoding                                                            |
| :------------------------------ | :--------------------------------------------------------------------------- |
| test-author writes tests        | `agent()` on session model, schema returns the file list, **no impl paths**  |
| RED check (tests must fail)     | `agent()` on `'haiku'`, runs the new tests, expects all-fail                 |
| review tests                    | `adversarialReview()` — diverse-lens panel + refutation vote                 |
| implement                       | `agent()` on session model, owns a non-overlapping file slice                |
| run tests + review impl         | `agent()` on `'haiku'` (run) + `adversarialReview()` (review)                |
| bounded fix loop                | `for` loop in the stage, ≤3 cycles                                           |
| regression between phases       | full-suite `agent()` on `'haiku'` between waves                              |
| integration / docs / final      | their own phases after the build waves                                       |

The win over turn-by-turn coordination: the loop, the branching, and every intermediate result live
in **script variables**, so the lead's context only ever sees the final return value.

## Authoring rules that keep the script correct

- **Plain JavaScript, not TypeScript.** No type annotations, interfaces, or generics — they fail to
  parse.
- **`meta` is a pure literal** — no variables, function calls, or interpolation. Use the same phase
  titles in `meta.phases` as in `phase()` / `opts.phase`.
- **No `Date.now()` / `Math.random()` / argless `new Date()`** — they throw (they'd break resume).
  Vary agent labels by index instead; pass any timestamp via `args`.
- **The script does no file or shell I/O** — only agents do. Anything the build must read or write
  goes in an agent prompt.
- **Use `schema` for anything you branch on** — validation happens at the tool layer, so the agent
  retries on mismatch and you get a clean object back instead of parsing prose.
- **Default to the session model** (omit `opts.model`); pass `model: 'haiku'` only on mechanical
  stages (running tests, scaffolding, docs).
- **Inside `parallel()`/`pipeline()` stages, set `opts.phase` explicitly** so agents land in the
  right progress group rather than racing on the global `phase()` state.

## The template

```js
export const meta = {
  name: 'build-FEATURE',                       // rename per build
  description: 'Implement FEATURE per the approved architecture: TDD with adversarial review',
  phases: [
    { title: 'Scaffold' },
    { title: 'Build' },
    { title: 'Integrate' },
    { title: 'Document' },
    { title: 'Verify' },
  ],
}

// ---------- schemas (branch only on validated data) ----------
const TESTS = { type: 'object', required: ['files'], properties: {
  files: { type: 'array', items: { type: 'string' } },
  summary: { type: 'string' } } }

const RUN = { type: 'object', required: ['passed'], properties: {
  passed: { type: 'boolean' }, total: { type: 'number' }, failed: { type: 'number' },
  unexpectedPasses: { type: 'array', items: { type: 'string' } },
  failures: { type: 'array', items: { type: 'object', properties: {
    test: { type: 'string' }, reason: { type: 'string' } } } } } }

const FINDINGS = { type: 'object', required: ['mustFix'], properties: {
  mustFix: { type: 'array', items: { type: 'object', required: ['title', 'detail'], properties: {
    title: { type: 'string' }, detail: { type: 'string' }, file: { type: 'string' } } } },
  shouldFix: { type: 'array', items: { type: 'string' } } } }

const VERDICT = { type: 'object', required: ['real'], properties: {
  real: { type: 'boolean' }, reason: { type: 'string' } } }

const HAIKU = 'haiku'   // cheap model for mechanical stages

// ---------- inputs from args (set in Step 4) ----------
// Provenance: if the architecture has a Build Manifest, populate args from it (see
// blueprint-and-roles.md → "Mapping the build manifest to args"); otherwise infer from the prose
// plan + File Structure + reconnaissance. Field-by-field: args.commands ← manifest.commands (or
// recon); each phase's implFiles ← manifest owns; waves ← manifest depends_on; ph.requirementRefs
// ← manifest requirement_refs; ui/ai/needsScaffold ← manifest flags; args.integration ←
// manifest integration_checkpoints.
// args.waves: ordered array of waves; each wave is an array of phase objects:
//   { name, requirementDocs[], requirementRefs[], archDocs[], interfaceDocs[], testPatternRefs[],
//     implFiles[], patternRefs[], ui:bool, ai:bool, designSystem }
// args.commands: { test, testOne(fileGlobs), typecheck, build }
// args.needsScaffold: bool ; args.scaffold: {prompt}
// args.integration: [{name, prompt}] ; args.docs: {prompt} ; args.designSystem: path|null

const W = args.waves
const C = args.commands

// ---------- one architecture phase, full TDD cycle ----------
async function buildPhase(ph) {
  // 1. tests — session model, information-isolated (NO impl paths in the prompt)
  const tests = await agent(
    `Write the unit/component tests for phase "${ph.name}".
     Read: requirements ${ph.requirementDocs?.join(', ')}; architecture interfaces ${ph.interfaceDocs?.join(', ')}.
     Follow the test patterns in ${ph.testPatternRefs?.join(', ')}.
     Acceptance criteria to assert against: ${ph.requirementRefs?.join(', ') || 'see the requirements docs'}.
     Cover the behaviors, edge cases, and error conditions the interfaces and those criteria imply.
     Do NOT read or reference any implementation files. Return the test file paths you created.`,
    { label: `tests:${ph.name}`, phase: 'Build', schema: TESTS })

  // 2. RED check — cheap model; every new test should FAIL
  const red = await agent(
    `Run only these test files and report results: ${tests.files.join(' ')}.
     Command base: ${C.testOne}. Expected: ALL FAIL (red step of TDD).
     Report any test that PASSED in unexpectedPasses[] — that means it tests the wrong thing or the
     feature already exists. Do not fix anything.`,
    { label: `red:${ph.name}`, phase: 'Build', model: HAIKU, schema: RUN })
  // (red.unexpectedPasses surfaces in the return; the lead investigates if non-empty)

  // 3. adversarial test-quality review
  const testReview = await adversarialReview({
    what: `the tests for phase "${ph.name}"`,
    read: `tests ${tests.files.join(', ')}; architecture interfaces ${ph.interfaceDocs?.join(', ')}; acceptance criteria in ${ph.requirementDocs?.join(', ')}`,
    ask: `Do the tests adequately cover the interfaces, edge cases, error conditions, and acceptance criteria? A MUST-FIX is a coverage gap that would let a wrong implementation pass.`,
  }, 'Build', `testreview:${ph.name}`)
  if (testReview.mustFix.length) {
    await agent(
      `Fix the tests for phase "${ph.name}" to address these gaps, without weakening existing coverage:
       ${JSON.stringify(testReview.mustFix)}. Return the updated test file paths.`,
      { label: `fix-tests:${ph.name}`, phase: 'Build', schema: TESTS })
  }

  // 4. implement + run + review, bounded fix loop
  const ui = ph.ui ? `Use the frontend-design skill.${ph.designSystem ? ` Honor the design system at ${ph.designSystem}.` : ''}` : ''
  let last = await agent(
    `Implement phase "${ph.name}" so its tests pass. You OWN these files only: ${ph.implFiles.join(', ')} — do not edit anything else.
     Read: architecture ${ph.archDocs?.join(', ')}; the tests ${tests.files.join(', ')}; pattern references ${ph.patternRefs?.join(', ')}.
     ${ui}
     Success: the phase tests pass, types check, the build succeeds.`,
    { label: `impl:${ph.name}`, phase: 'Build' })

  let surviving = []
  for (let cycle = 0; cycle < 3; cycle++) {
    const run = await agent(
      `Run the full test suite and report results. Command: ${C.test}. Expected: ALL PASS. Do not fix anything.`,
      { label: `run:${ph.name}#${cycle}`, phase: 'Build', model: HAIKU, schema: RUN })
    const review = await adversarialReview({
      what: `the implementation of phase "${ph.name}"`,
      read: `implementation ${ph.implFiles.join(', ')}; architecture ${ph.archDocs?.join(', ')}; tests ${tests.files.join(', ')}; requirements ${ph.requirementDocs?.join(', ')}; acceptance criteria ${ph.requirementRefs?.join(', ') || '(see requirements)'}`,
      ask: `Does the implementation match the architecture and satisfy the spec? Check edge cases, error handling, type safety, security, and pattern adherence. A MUST-FIX is a blocking deviation from the architecture or spec.`,
    }, 'Build', `review:${ph.name}#${cycle}`)
    surviving = review.mustFix
    if (run.passed && surviving.length === 0) break
    last = await agent(
      `Fix phase "${ph.name}". Failing tests: ${JSON.stringify(run.failures || [])}.
       Blocking review findings: ${JSON.stringify(surviving)}.
       Edit only your owned files: ${ph.implFiles.join(', ')}.`,
      { label: `fix:${ph.name}#${cycle}`, phase: 'Build' })
  }
  return { phase: ph.name, tests: tests.files, files: ph.implFiles,
           unexpectedPasses: red.unexpectedPasses || [], unresolvedMustFix: surviving }
}

// ---------- run ----------
phase('Scaffold')
if (args.needsScaffold) {
  await agent(args.scaffold.prompt, { label: 'scaffold', phase: 'Scaffold', model: HAIKU })
}

phase('Build')
const phaseResults = []
for (let w = 0; w < W.length; w++) {
  // phases within a wave are independent → run concurrently (capped at 16 automatically)
  const wave = await parallel(W[w].map(ph => () => buildPhase(ph)))
  phaseResults.push(...wave.filter(Boolean))
  // between-wave regression — a later wave must not break earlier work
  if (w < W.length - 1) {
    const reg = await agent(
      `Run the FULL test suite (all waves so far) plus a typecheck. Commands: ${C.test}; ${C.typecheck}.
       Expected: ALL PASS. Report any failure as a regression. Do not fix anything.`,
      { label: `regression:wave${w + 1}`, phase: 'Build', model: HAIKU, schema: RUN })
    if (!reg.passed) {
      log(`Regression after wave ${w + 1}: ${reg.failed} failing. Repairing before next wave.`)
      // repair the regression with a focused implement+verify pass before continuing
      await agent(
        `Earlier-wave tests now fail after wave ${w + 1}: ${JSON.stringify(reg.failures)}.
         Identify the offending change and fix it so all tests pass again. Keep within the files the build owns.`,
        { label: `repair:wave${w + 1}`, phase: 'Build' })
    }
  }
}

phase('Integrate')
const integration = []
for (const seam of (args.integration || [])) {
  const t = await agent(
    `${seam.prompt}\nYou MAY read implementation code (integration tests need to know what's built).
     Write integration tests across the seam, then run them and report results. Command: ${C.test}.`,
    { label: `integration:${seam.name}`, phase: 'Integrate', schema: RUN })
  integration.push({ name: seam.name, passed: t.passed, failures: t.failures || [] })
}

phase('Document')
if (args.docs) {
  await agent(
    `${args.docs.prompt}\nWrite documentation reflecting what was actually built. Do not modify implementation code.`,
    { label: 'docs', phase: 'Document', model: HAIKU })
}

phase('Verify')
const final = await agent(
  `Final verification. Run, in order: tests (${C.test}), typecheck (${C.typecheck}), build (${C.build}).
   Expected: ALL PASS / clean. Report the status of each and any failures. Do not fix anything.`,
  { label: 'final-verification', phase: 'Verify', model: HAIKU, schema: RUN })

return { phases: phaseResults, integration, finalVerification: final,
         openIssues: phaseResults.flatMap(p => p.unresolvedMustFix.map(f => ({ phase: p.phase, ...f }))) }
```

## Adversarial review with refutation voting

This is the chosen verification design: a diverse-lens panel surfaces candidate blocking issues,
then each candidate must survive a refutation vote before it counts. It rejects plausible-but-wrong
findings that a single reviewer would wave through, and confirms the real ones from independent
angles. Add it alongside the template:

```js
const LENSES = [
  'architecture-compliance: does it match the component design, interfaces, and technical decisions?',
  'spec & acceptance-criteria: does it satisfy the requirements and business rules?',
  'edge-cases & error-handling: boundaries, failure paths, invalid input, missing error handling?',
  'security: injection, authz/authn gaps, unsafe data handling, secret leakage?',
]

async function adversarialReview({ what, read, ask }, ph, label) {
  // 1. diverse-lens panel → union of candidate blocking findings
  const panels = await parallel(LENSES.map((lens, i) => () =>
    agent(`Review ${what} through ONE lens — ${lens}\nRead: ${read}.\n${ask}\nReport only blocking (MUST-FIX) issues for your lens; list quality nits as shouldFix.`,
      { label: `${label}:L${i + 1}`, phase: ph, schema: FINDINGS })))
  const candidates = panels.filter(Boolean).flatMap(p => p.mustFix)
  const shouldFix = panels.filter(Boolean).flatMap(p => p.shouldFix || [])
  if (!candidates.length) return { mustFix: [], shouldFix }

  // 2. refutation vote — keep a finding only if a majority of skeptics confirm it's real
  const judged = await parallel(candidates.map((f, i) => () =>
    parallel([0, 1, 2].map(j => () =>
      agent(`A reviewer claims this is a blocking issue in ${what}:\nTITLE: ${f.title}\nDETAIL: ${f.detail}\nFILE: ${f.file || 'n/a'}\nRead: ${read}.\nTry to REFUTE it. Default real=false unless you can confirm it genuinely violates the architecture or spec.`,
        { label: `${label}:refute${i + 1}.${j + 1}`, phase: ph, model: HAIKU, schema: VERDICT })))
      .then(vs => ({ f, real: vs.filter(Boolean).filter(v => v.real).length >= 2 }))))
  return { mustFix: judged.filter(j => j.real).map(j => j.f), shouldFix }
}
```

Notes:
- The panel runs on the **session model** (real judgment); the refutation skeptics run on
  **`'haiku'`** — they're checking a single concrete claim, which the cheap model does well and
  cheaply across many findings.
- Scale the panel to the stakes: 4 lenses + 3-vote refutation is the default for a normal build. For
  a quick single-phase run you can drop to 2 lenses and a single confirming reviewer; for a
  high-stakes security-sensitive build, add lenses or raise the vote threshold.

## Worktree isolation (only when agents collide)

By default the **file-ownership map prevents collisions** — partition `implFiles` so no two
concurrently-running agents touch the same file, and you need no worktrees. Reach for
`isolation: 'worktree'` **only** when two agents in the *same wave* genuinely must mutate the same
file and you can't serialize them into different waves. Worktrees are expensive (~200–500ms + disk
per agent) and leave you to merge the results, so prefer partitioning or serialization first.

```js
await agent(prompt, { label: `impl:${ph.name}`, phase: 'Build', isolation: 'worktree' })
```

## Parameterizing with args, rerun, and resume

- **Pass `args` as real JSON** in the Workflow call (`args: { waves: [...], commands: {...} }`), not
  a stringified blob — a string breaks `args.waves.map(...)` in the script.
- **Scope = one phase:** set `args.waves` to a single wave with that one phase; skip scaffold,
  integration, and docs as appropriate. Same script, smaller scope.
- **Rerun on a new scope:** the Workflow tool persists the script and returns its `scriptPath`.
  Re-invoke with `{ scriptPath, args: <new scope> }` rather than resending the script.
- **Resume after a stop (same session):** re-invoke with `{ scriptPath, resumeFromRunId: <id> }` —
  completed agents return cached results; only new/edited calls re-run. Stop the prior run first.
