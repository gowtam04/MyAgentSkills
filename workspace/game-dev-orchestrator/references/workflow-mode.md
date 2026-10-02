# Workflow Mode — the game build as a background script

Instead of coordinating turn by turn, you write a dynamic Workflow script that runs the whole
blueprint build in the background. The script holds the loop, the branching and every intermediate
result, so your context only receives the final return value.

## Contents
- [When to use it](#when-to-use-it)
- [What changes from subagent mode](#what-changes-from-subagent-mode)
- [Before launch](#before-launch)
- [Building args](#building-args)
- [The script](#the-script)
- [After it returns](#after-it-returns)

## When to use it

- The user chose it at kickoff, or asked for a hands-off or background build.
- It suits large blueprints (roughly 6+ phases) whose plan is complete. A running workflow can't
  ask anything, so every decision must be settled before launch — including the art fallback for
  any `image-gen` asset.
- Choosing this mode at kickoff counts as the explicit opt-in the Workflow tool requires.

## What changes from subagent mode

| Subagent mode | Workflow mode |
|---|---|
| You check each review finding against the code (or the image), and read judgment-heavy/high-risk diffs yourself | Skeptic agents try to refute each finding (one per finding normally, three with majority vote for judgment-heavy and `risk: high` phases); you read those phases' diffs after the run returns |
| You settle test disputes | A judge agent rules: `test-wrong`, `code-wrong`, or `gdd-ambiguous` (which blocks the phase) |
| Blockers go to the user mid-build | Blockers stop that phase and its dependents; everything else continues, and blockers come back in the result |
| Fix rounds continue the same worker (`SendMessage`) | Each fix round is a fresh agent given the full phase brief plus what's still open |
| Worktrees for parallel implementers | Shared tree with disjoint ownership. Merges need judgment the script can't exercise |
| You run git | One serialized "git operator" agent at a time, explicit paths only |
| Checkpoint failures: you decide which side is wrong | Reported in the result; you resolve them after the run, in subagent mode |
| `needs-human` items go in the progress file as they come | Collected from every playtest and returned in the result |

Everything else is the same: spec-first tests committed before implementation, implementers who
can't edit tests, the style lock before every other asset, MUST-FIX and SHOULD-FIX both blocking, a
cap of 3 fix rounds, regression with in-flight files marked expected, the traceability check at
review and final verification, screenshot playtests, and a commit per verified phase.

Runtime limits: about `min(16, CPUs − 2)` agents run at once (the rest queue), a run is capped at
1,000 agents in total, and resume works only within the same Claude Code session.

## Before launch

1. Steps 1–2 of the main skill: read the blueprint, validate the manifest, pre-flight, baseline.
2. The permission choice from kickoff matters even more here. Workflow agents run in `acceptEdits`
   mode, so file edits don't prompt, but shell commands that aren't allowlisted — tests, the
   screenshot script, art generator scripts, `asset_qa.py` — will prompt mid-run and stall the
   workflow.
3. Write the initial progress file yourself. The script can't touch files.
4. Build `args` (below) and call **Workflow** with the script inline and `args` as real JSON (not a
   stringified blob). The user approves the launch card; the run proceeds in the background.

## Building args

Built from the manifest and the docs you read:

```js
{
  root: "/abs/project/root",
  skillDir: "/abs/path/to/game-dev-orchestrator",  // agents read personas and scripts from here
  planDoc: "docs/game-architecture/implementation-plan.md",   // the doc holding the manifest
  mode: "PM",                                      // or "Developer"
  conventions: [],                                 // Developer mode: conventions + testing-and-playtest paths
  archDocs: ["docs/game-architecture/overview.md", "docs/game-architecture/systems-and-interfaces.md"],
  artDirection: "docs/gdd/06-art-audio-juice.md",
  commands: { test: "...", test_one: "... {files}", typecheck: "...", build: "...", smoke: "...",
              screenshot: "..." },
  models: {                                        // Model routing (main skill); change only if the user asked
    writer: "opus", writerHigh: "opus", impl: "sonnet", implHigh: "opus", review: "opus",
    skeptic: "sonnet", runner: "haiku", integration: "opus", playtester: "opus",
    artistLock: "opus", artist: "sonnet", content: "sonnet", docs: "sonnet"
  },
  phases: [{
    id: "p4a", name: "Drop rules", kind: "gameplay", risk: "high", depends_on: ["p2"],
    owns: ["src/rules/drop.ts"], tests: ["tests/rules/drop.test.ts"], shared: [],
    refs: ["docs/gdd/03-systems.md#drop"], testFocus: "...", playtestFocus: "",   // "" when none
    gddDocs: ["docs/gdd/03-systems.md"],
    interfaceDocs: ["docs/game-architecture/systems-and-interfaces.md#drop"],
    archDocs: [], exemplars: [], testExemplars: [],
    judgment: true,                                // your kickoff classification: judgment-heavy → implHigh
    checks: "",                                    // non-test kinds: the verification command(s)
    styleLock: false,                              // true for the style-lock phase (Opus artist)
    assets: []                                     // assets phases: the Asset Manifest rows it owns
  }],
  checkpoints: [{ name: "loop-playable", after: ["p6"], verifies: "...",
                  folder: "tests/integration/loop-playable", integration: true }],
  slice: { verifies: "the full vertical slice from the GDD", gdd: "docs/gdd/01-vision.md#vertical-slice" },
  docs: { prompt: "README setup/run/test/export, how to play, how to add a level" }   // or null
}
```

For non-test kinds, set `checks` to the commands the kind calls for: build, smoke and screenshot
for `scaffold`/`wiring`, typecheck for `contracts`, the validation command for `content`, the
`asset_qa.py` run for `assets`. Set `integration: false` on a checkpoint whose phases are all
assets.

## The script

Adapt it rather than writing orchestration from scratch. It's plain JavaScript: no type
annotations, no `Date.now()`/`Math.random()`, and no file or shell access from the script itself
(only agents do I/O).

```js
export const meta = {
  name: 'game-dev-orchestrator',
  description: 'Build the approved game architecture: spec-first tests, implementation, art, verified review, playtests, docs, final verification',
  phases: [
    { title: 'Build', detail: 'each phase starts when its dependencies verify: tests → implement or produce → review → fix → regression → playtest → commit' },
    { title: 'Checkpoints', detail: 'integration tests and playtests at each checkpoint' },
    { title: 'Document' },
    { title: 'Verify', detail: 'full test, typecheck, build, smoke, screenshot, slice playtest' },
  ],
}

const A = args
const C = A.commands
const M = A.models
const PHASES = A.phases
const byId = Object.fromEntries(PHASES.map(p => [p.id, p]))
const status = {}                 // id -> { state: 'verified' | 'blocked' | 'skipped' | 'failed', ... }
const started = new Set()
const needsHuman = []

// ---------- schemas
const STR = { type: 'string' }
const LIST = { type: 'array', items: STR }
const TESTS = { type: 'object', required: ['files', 'unexpectedPasses'], properties: {
  files: LIST, coveredRefs: LIST, unexpectedPasses: LIST, gaps: LIST, blocked: STR } }
const IMPL = { type: 'object', required: ['filesChanged', 'checksPass'], properties: {
  filesChanged: LIST, checksPass: { type: 'boolean' }, blocked: STR,
  disputes: { type: 'array', items: { type: 'object', required: ['test', 'reason'],
    properties: { test: STR, reason: STR, citation: STR } } } } }
const FINDING = { type: 'object', required: ['title', 'detail'], properties: {
  title: STR, detail: STR, file: STR, line: { type: 'number' } } }
const FINDINGS = { type: 'object', required: ['mustFix', 'shouldFix'], properties: {
  mustFix: { type: 'array', items: FINDING }, shouldFix: { type: 'array', items: FINDING } } }
const VERDICT = { type: 'object', required: ['real'], properties: { real: { type: 'boolean' }, reason: STR } }
const RULINGS = { type: 'object', required: ['rulings'], properties: { rulings: { type: 'array', items: {
  type: 'object', required: ['test', 'ruling'], properties: { test: STR, reason: STR,
    ruling: { type: 'string', enum: ['test-wrong', 'code-wrong', 'gdd-ambiguous'] } } } } } }
const RUN = { type: 'object', required: ['passed'], properties: {
  passed: { type: 'boolean' }, total: { type: 'number' }, failed: { type: 'number' },
  unexpectedFailures: { type: 'array', items: { type: 'object', properties: { file: STR, test: STR, reason: STR } } },
  expectedFailures: LIST, unexpectedPasses: LIST, typecheck: STR, build: STR, smoke: STR, screenshot: STR } }
const PLAY = { type: 'object', required: ['passed'], properties: {
  passed: { type: 'boolean' }, boot: STR, evidence: LIST,
  criteria: { type: 'array', items: { type: 'object', required: ['criterion', 'result'], properties: {
    criterion: STR, result: { type: 'string', enum: ['PASS', 'FAIL', 'NEEDS-HUMAN'] }, evidence: STR, tryThis: STR } } } } }
const GIT = { type: 'object', required: ['ok'], properties: { ok: { type: 'boolean' }, commit: STR, detail: STR } }

// ---------- shared prompt pieces
const persona = role => `First read and follow ${A.skillDir}/references/personas/${role}.md.`
const WORKER = `Project root: ${A.root}. You are not alone: other agents are editing other files right now — don't revert edits you didn't make. Don't run git commands that change state; a git operator handles git.`
const testOne = files => C.test_one.replace('{files}', files.join(' '))
const inFlight = except => PHASES
  .filter(p => started.has(p.id) && status[p.id]?.state !== 'verified' && p.id !== except)
  .flatMap(p => [...(p.tests || []), ...(p.owns || [])])
const verifiedTests = () => PHASES.filter(p => status[p.id]?.state === 'verified').flatMap(p => p.tests || [])
const TRACE = `${A.skillDir}/scripts/check_traceability.py`
const QA = `${A.skillDir}/scripts/asset_qa.py`
const ASSETDOC = `${A.skillDir}/references/asset-production.md`

// ---------- git: one operator at a time, explicit paths only
let gitQueue = Promise.resolve()
function git(task, label, ph) {
  const step = gitQueue.then(() => agent(
    `You are the build's git operator in ${A.root}. ${task}
Stage explicit paths only — never "git add -A" or "git add .". Don't modify file contents. Return the commit hash.`,
    { label, phase: ph, model: M.runner, schema: GIT }))
  gitQueue = step.catch(() => null)
  return step
}

// ---------- review: reviewer(s), then skeptics try to refute each finding
const LENSES = [
  'GDD: every cited rule is implemented and tested, no player verb, number or juice beyond the GDD is invented, and the test files are unchanged since their commit',
  'architecture: interfaces, scene model, data formats, tunables-in-data and technical decisions match the architecture docs',
  'edge cases, timing and determinism: boundaries, frame-rate dependence, float rounding, state machine holes, pause and time scale, seeded randomness',
]
const ASSET_LENS = `asset review: view every image and contact sheet with the Read tool; check size, transparency, palette (run python3 ${QA}), silhouette at 1x game scale, frame alignment, tile seams and style-lock match against the Asset Manifest rows`
async function review(ph, what, read, label) {
  const high = ph.risk === 'high' || ph.judgment
  const lenses = ph.kind === 'assets' ? [ASSET_LENS] : high ? LENSES : ['all of these — ' + LENSES.join('; ')]
  const panels = await parallel(lenses.map((lens, i) => () => agent(
    `${persona('reviewer')}\n${WORKER}\nReview ${what} for phase ${ph.id} "${ph.name}" through this lens: ${lens}.
Read: ${read}. gdd_refs: ${ph.refs.join(', ') || 'none'}.
Report MUST-FIX and SHOULD-FIX findings with file, line and evidence. Both block, so don't file taste preferences.`,
    { label: `${label}:L${i + 1}`, phase: 'Build', model: M.review, schema: FINDINGS })))
  const claims = panels.filter(Boolean).flatMap(p => [
    ...p.mustFix.map(f => ({ ...f, severity: 'MUST-FIX' })),
    ...p.shouldFix.map(f => ({ ...f, severity: 'SHOULD-FIX' }))])
  const votes = high ? 3 : 1
  const judged = await parallel(claims.map((f, i) => () =>
    parallel(Array.from({ length: votes }, (_, j) => () => agent(
      `A reviewer claims this ${f.severity} issue in phase "${ph.name}": ${f.title} — ${f.detail} (${f.file || 'n/a'}:${f.line || '?'}).
Read the cited code or view the cited image, and for context: ${read}. Try to refute it — is it wrong, already handled, or outside this phase? Answer real=true only if the work genuinely has this problem.`,
      { label: `${label}:check${i + 1}.${j + 1}`, phase: 'Build', model: M.skeptic, schema: VERDICT })))
      .then(vs => ({ f, real: vs.filter(Boolean).filter(v => v.real).length * 2 > votes }))))
  return judged.filter(Boolean).filter(j => j.real).map(j => j.f)
}

// ---------- playtest: a playtester runs the pinned commands and views the screenshots
async function playtest(label, criteria, refs, folder, ph) {
  const res = await agent(`${persona('playtester')}\n${WORKER}
Run: ${C.smoke}; then ${C.screenshot}. Save evidence under ${folder}.
Judge each criterion from what the screenshots, logs and debug state actually show: ${criteria}.
gdd_refs: ${refs.join(', ') || 'none'}. Use NEEDS-HUMAN for feel, timing, audio and haptics, and say what a human should try.`,
    { label, phase: ph, model: M.playtester, schema: PLAY })
  for (const c of (res && res.criteria) || []) {
    if (c.result === 'NEEDS-HUMAN') needsHuman.push({ at: label, criterion: c.criterion, tryThis: c.tryThis || '' })
  }
  return res
}

// ---------- one phase, end to end
async function buildPhase(ph) {
  started.add(ph.id)
  const testFirst = (ph.tests || []).length > 0
  const docs = `GDD ${ph.gddDocs.join(', ')}; interfaces ${ph.interfaceDocs.join(', ')}` +
    (A.conventions.length ? `; conventions ${A.conventions.join(', ')}` : '')
  const stop = (state, reason, extra) => (status[ph.id] = { state, reason, ...(extra || {}) })

  // 1. spec-first tests, then lock them in a commit
  let testFiles = []
  if (testFirst) {
    const writerPrompt = `${persona('test-writer')}\n${WORKER}
Phase ${ph.id} "${ph.name}". gdd_refs: ${ph.refs.join(', ')}. Test focus: ${ph.testFocus}.
Read: ${docs}. Style references only: ${ph.testExemplars.join(', ') || 'none'}.
You own ONLY: ${ph.tests.join(', ')}. Never open implementation files. Tag every test with its gdd: tags.
Run your tests with: ${testOne(ph.tests)} — they should fail. Report unexpected passes.
If a rule is too ambiguous to test, set "blocked" to the question.`
    const t = await agent(writerPrompt, { label: `tests:${ph.id}`, phase: 'Build',
      model: ph.risk === 'high' ? M.writerHigh : M.writer, schema: TESTS })
    if (!t) return stop('failed', 'test-writer died')
    if (t.blocked) return stop('blocked', `GDD question: ${t.blocked}`)
    testFiles = t.files
    await git(`git add ${testFiles.join(' ')} && git commit -m "test(${ph.id}): spec tests for ${ph.name}"`, `git:tests:${ph.id}`, 'Build')

    if (ph.risk === 'high' || A.mode === 'Developer') {
      for (let r = 0; r < 2; r++) {
        const issues = await review(ph, 'the spec tests, before implementation', `tests ${testFiles.join(', ')}; ${docs}`, `testreview:${ph.id}#${r}`)
        if (!issues.length) break
        await agent(`${writerPrompt}\n\nFix round: address these issues without weakening coverage: ${JSON.stringify(issues)}`,
          { label: `fix-tests:${ph.id}#${r}`, phase: 'Build', model: M.writerHigh, schema: TESTS })
        await git(`git add ${testFiles.join(' ')} && git commit -m "test(${ph.id}): address test review"`, `git:testfix:${ph.id}#${r}`, 'Build')
      }
    }
  }

  // 2. implement, produce art, or author content — the tests stay read-only
  const check = testFirst ? [testOne(testFiles), ph.checks].filter(Boolean).join('; then ') : ph.checks
  const own = `Own (edit nothing else): ${ph.owns.join(', ')}${(ph.shared || []).length ? `; shared, you're its only writer now: ${ph.shared.join(', ')}` : ''}.`
  let role, workPrompt, model, highModel
  if (ph.kind === 'assets') {
    role = 'asset-artist'
    model = ph.styleLock ? M.artistLock : M.artist
    highModel = M.artistLock
    workPrompt = `${persona('asset-artist')}\n${WORKER}
Produce phase ${ph.id} "${ph.name}"${ph.styleLock ? ' — this is the STYLE LOCK every later asset copies' : ''}. gdd_refs: ${ph.refs.join(', ') || 'none'}.
Asset Manifest rows: ${JSON.stringify(ph.assets)}. Read ${ASSETDOC} and the art direction in ${A.artDirection}.
${ph.styleLock ? '' : 'Work from the style lock (read-only): its palette, rules note and reference sheet.'}
Verify every asset by viewing it and with: python3 ${QA}. ${ph.checks ? `Also run: ${ph.checks}.` : ''}
${own} If the assigned method can't reach the spec, or a needed image-gen tool is missing, set "blocked".`
  } else {
    role = ph.kind === 'content' ? 'content-author' : 'implementer'
    model = ph.risk === 'high' || ph.judgment ? M.implHigh : role === 'content-author' ? M.content : M.impl
    highModel = M.implHigh
    workPrompt = `${persona(role)}\n${WORKER}
${role === 'content-author' ? 'Author the content for' : 'Implement'} phase ${ph.id} "${ph.name}" (${ph.kind}). gdd_refs: ${ph.refs.join(', ') || 'none'}.
Read: architecture ${[...A.archDocs, ...ph.archDocs].join(', ')}; ${docs}; exemplars ${ph.exemplars.join(', ') || 'none'}.
${testFirst ? `Make these tests pass. Read them; never edit, skip or weaken them: ${testFiles.join(', ')}.` : ''}
Verify with: ${check || 'the checks your role calls for'}.
${own}
If a test looks wrong, list it under disputes with the GDD text. If a rule or number you need is missing, set "blocked".`
  }
  let work = await agent(workPrompt, { label: `${role}:${ph.id}`, phase: 'Build', model, schema: IMPL })
  if (!work) return stop('failed', `${role} died`)
  if (work.blocked) return stop('blocked', `${role}: ${work.blocked}`)

  // 3. test disputes: a judge rules against the GDD
  if ((work.disputes || []).length) {
    const r = await agent(`Rule on these disputes between the spec tests and the ${role} for phase "${ph.name}": ${JSON.stringify(work.disputes)}.
Read the tests, the cited GDD text in ${ph.gddDocs.join(', ')}, and ${ph.interfaceDocs.join(', ')}. For each: test-wrong, code-wrong, or gdd-ambiguous (the GDD genuinely doesn't settle it).`,
      { label: `judge:${ph.id}`, phase: 'Build', model: M.review, schema: RULINGS })
    const rulings = (r && r.rulings) || []
    const ambiguous = rulings.filter(x => x.ruling === 'gdd-ambiguous')
    if (ambiguous.length) return stop('blocked', 'gdd-ambiguous test disputes', { disputes: ambiguous })
    const wrongTests = rulings.filter(x => x.ruling === 'test-wrong')
    if (wrongTests.length) {
      await agent(`${persona('test-writer')}\n${WORKER}\nA judge ruled these tests wrong against the GDD: ${JSON.stringify(wrongTests)}. Fix only those tests. Own only: ${ph.tests.join(', ')}.`,
        { label: `fix-tests:${ph.id}:ruling`, phase: 'Build', model: M.writerHigh, schema: TESTS })
      await git(`git add ${testFiles.join(' ')} && git commit -m "test(${ph.id}): correct tests per ruling"`, `git:ruling:${ph.id}`, 'Build')
    }
    work = await agent(`${workPrompt}\n\nRulings on your disputes: ${JSON.stringify(rulings)}. Where the code was ruled wrong, change the code.`,
      { label: `${role}:${ph.id}:after-ruling`, phase: 'Build', model, schema: IMPL }) || work
  }

  // 4. run + review + fix, both severities, max 3 rounds
  const read = ph.kind === 'assets'
    ? `the produced assets under ${ph.owns.join(', ')}, the style lock, the Asset Manifest rows ${JSON.stringify(ph.assets)}, ${A.artDirection}`
    : `the phase's changes (git diff -- ${ph.owns.join(' ')})${testFiles.length ? `, tests ${testFiles.join(', ')}` : ''}, ${docs}`
  const trace = testFirst ? `. Also run python3 ${TRACE} ${A.planDoc} --root ${A.root} --phase ${ph.id} — a cited gdd_ref no test is tagged with is a MUST-FIX` : ''
  let run = null
  let open = []
  for (let round = 0; round < 3; round++) {
    run = check ? await agent(`${persona('test-runner')}\nRun: ${check}. Expected: all-pass.`,
      { label: `run:${ph.id}#${round}`, phase: 'Build', model: M.runner, schema: RUN }) : { passed: true }
    open = await review(ph, ph.kind === 'assets' ? 'the produced assets' : 'the implementation', `${read}${trace}`, `review:${ph.id}#${round}`)
    if (run && run.passed && !open.length) break
    if (round === 2) break
    // escalate on failure: the last fix round runs a tier up
    await agent(`${workPrompt}\n\nFix round ${round + 1}. Failing checks: ${JSON.stringify((run && run.unexpectedFailures) || [])}.
Verified findings — fix every one, MUST-FIX and SHOULD-FIX alike: ${JSON.stringify(open)}`,
      { label: `fix:${ph.id}#${round}`, phase: 'Build', model: round >= 1 ? highModel : model, schema: IMPL })
  }
  if (!(run && run.passed) || open.length) return stop('blocked', 'still open after 3 rounds', { open, failures: run && run.unexpectedFailures })

  // 5. regression over everything verified so far
  if (ph.kind !== 'assets') {
    const expected = inFlight(ph.id)
    const regCmd = `${testOne([...verifiedTests(), ...testFiles])}; then ${C.typecheck}`
    let reg = await agent(`${persona('test-runner')}\nRun: ${regCmd}.
Expected: all-pass, except failures confined to these in-flight files, which you list under expectedFailures: ${expected.join(', ') || 'none'}.`,
      { label: `regression:${ph.id}`, phase: 'Build', model: M.runner, schema: RUN })
    if (!(reg && reg.passed)) {
      await agent(`${workPrompt}\n\nRegression: earlier-phase checks now fail: ${JSON.stringify((reg && reg.unexpectedFailures) || [])}.
Fix it within your owned files. If the fix needs another phase's file, set "blocked" and explain.`,
        { label: `repair:${ph.id}`, phase: 'Build', model, schema: IMPL })
      reg = await agent(`${persona('test-runner')}\nRun: ${regCmd}. Expected: all-pass except failures confined to: ${expected.join(', ') || 'none'}.`,
        { label: `regression:${ph.id}#2`, phase: 'Build', model: M.runner, schema: RUN })
      if (!(reg && reg.passed)) return stop('blocked', 'regression', { failures: reg && reg.unexpectedFailures })
    }
  }

  // 6. playtest when the phase has a focus, then commit
  let play = null
  if (ph.playtestFocus) {
    play = await playtest(`playtest:${ph.id}`, ph.playtestFocus, ph.refs, `tmp/playtest/${ph.id}`, 'Build')
    if (!(play && play.passed)) return stop('blocked', 'playtest failed', { playtest: play })
  }
  const verb = ph.kind === 'gameplay' ? 'feat' : ph.kind === 'assets' ? 'art' : ph.kind === 'content' ? 'content' : ph.kind === 'docs' ? 'docs' : 'chore'
  const commit = await git(`git add ${[...ph.owns, ...(ph.shared || [])].join(' ')} && git commit -m "${verb}(${ph.id}): ${ph.name}"`, `git:phase:${ph.id}`, 'Build')
  return stop('verified', '', { commit: commit && commit.commit, tests: testFiles, playtest: play })
}

// ---------- schedule: each phase starts the moment its dependencies verify
const runs = {}
function runPhase(id) {
  if (!runs[id]) runs[id] = (async () => {
    const ph = byId[id]
    await Promise.all((ph.depends_on || []).map(runPhase))
    const waiting = (ph.depends_on || []).filter(d => status[d]?.state !== 'verified')
    if (waiting.length) return (status[id] = { state: 'skipped', reason: `depends on unverified ${waiting.join(', ')}` })
    try { return await buildPhase(ph) } catch (e) { return (status[id] = { state: 'failed', reason: String(e) }) }
  })()
  return runs[id]
}

phase('Build')
await parallel(PHASES.map(p => () => runPhase(p.id)))
const blocked = Object.entries(status).filter(([, s]) => s.state !== 'verified')
if (blocked.length) log(`${blocked.length} phase(s) not verified: ${blocked.map(([id, s]) => `${id} (${s.state})`).join(', ')}`)

phase('Checkpoints')
const checkpoints = await parallel((A.checkpoints || []).map(cp => async () => {
  const notReady = cp.after.filter(d => status[d]?.state !== 'verified')
  if (notReady.length) return { name: cp.name, state: 'skipped', reason: `unverified: ${notReady.join(', ')}` }
  const refs = cp.after.flatMap(id => byId[id].refs)
  const [seams, play] = await parallel([
    () => cp.integration ? agent(`${persona('integration-tester')}\n${WORKER}
Checkpoint "${cp.name}" — prove: ${cp.verifies}. gdd_refs: ${refs.join(', ')}. Read ${A.archDocs.join(', ')} and the implementation of phases ${cp.after.join(', ')}.
Write tests only under ${cp.folder}, tagged with gdd: tags. Run them (${C.test_one.replace('{files}', cp.folder)}), ${C.smoke} and ${C.screenshot}; look at the screenshots.`,
      { label: `integration:${cp.name}`, phase: 'Checkpoints', model: M.integration, schema: RUN }) : Promise.resolve({ passed: true }),
    () => playtest(`playtest:${cp.name}`, cp.verifies, refs, `tmp/playtest/${cp.name}`, 'Checkpoints'),
  ])
  if (cp.integration && seams && seams.passed) await git(`git add ${cp.folder} && git commit -m "test(integration): ${cp.name}"`, `git:int:${cp.name}`, 'Checkpoints')
  return { name: cp.name, integration: seams, playtest: play,
    passed: !!(seams && seams.passed && play && play.passed) }
}))

phase('Document')
if (A.docs) {
  await agent(`${persona('docs-writer')}\n${WORKER}\n${A.docs.prompt}\nDocument what was actually built. Don't change code behavior.`,
    { label: 'docs', phase: 'Document', model: M.docs })
  await git(`Stage only documentation files the docs writer changed (README, docs/, docstring-only changes) and commit with "docs: build documentation".`, 'git:docs', 'Document')
}

phase('Verify')
const integrationGlobs = (A.checkpoints || []).filter(cp => cp.integration).map(cp => `"${cp.folder}/**"`).join(' ')
const final = await agent(`${persona('test-runner')}\nFinal verification, in order: ${C.test}; ${C.typecheck}; ${C.build}; ${C.smoke}; ${C.screenshot}; python3 ${TRACE} ${A.planDoc} --root ${A.root}${integrationGlobs ? ' --extra-tests ' + integrationGlobs : ''}. Expected: all-pass (the traceability check exits 0 when every cited gdd_ref of a tested phase is proven by a tagged test). Report typecheck, build, smoke, screenshot and traceability status.`,
  { label: 'final-verification', phase: 'Verify', model: M.runner, schema: RUN })
const slice = A.slice ? await playtest('playtest:slice', A.slice.verifies, [A.slice.gdd], 'tmp/playtest/slice', 'Verify') : null

return { status, checkpoints, finalVerification: final, slicePlaytest: slice, needsHuman,
  notVerified: blocked.map(([id, s]) => ({ id, ...s })) }
```

Notes:
- **Review scale** follows the main skill: one reviewer plus one skeptic per finding for normal
  phases, a three-lens panel plus three skeptics for judgment-heavy and `risk: high` phases. Asset
  phases always get the asset-review lens.
- **The style lock gates art** through `depends_on`: every asset-family phase depends on the
  style-lock phase, so it starts the moment the lock verifies.
- **Scope = one phase or a subset:** pass only those phases in `args.phases` (and drop
  checkpoints/docs as appropriate). Verified dependencies outside the subset must already be
  committed; leave them out of `depends_on`.
- **Iterate on the script:** edit the persisted file the Workflow tool returned and re-invoke with
  `{ scriptPath }`. **Resume after a stop** in the same session: `{ scriptPath, resumeFromRunId }`,
  so completed agents return cached results.

## After it returns

1. Read the result, then check it the way you'd check any report. Read the diff of every
   judgment-heavy and `risk: high` phase yourself — the lead review the script couldn't do mid-run —
   view a few produced assets and playtest screenshots, and spot-check the test-lock
   (`git diff <test commit> -- <tests>`). Findings go to the owning worker in subagent mode. Re-run
   final verification with a fresh runner if the result looks surprising.
2. Write the final progress file from the returned data, including every `needsHuman` item.
3. Handle what's open in subagent mode: blocked phases go to the user with one AskUserQuestion card
   of options; checkpoint failures go to the owning implementers; skipped phases resume once their
   dependencies are fixed.
4. Report as in step 7 of the main skill. Say plainly which parts the workflow verified and which
   are still open.
