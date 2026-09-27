# Workflow Mode — the build as a background script

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
  ask anything, so every decision must be settled before launch.
- Choosing this mode at kickoff counts as the explicit opt-in the Workflow tool requires.

## What changes from subagent mode

| Subagent mode | Workflow mode |
|---|---|
| You check each review finding against the code, and read judgment-heavy/high-risk diffs yourself | Skeptic agents try to refute each finding (one per finding normally, three with majority vote for judgment-heavy and `risk: high` phases); you read those phases' diffs after the run returns |
| You settle test disputes | A judge agent rules: `test-wrong`, `code-wrong`, or `spec-ambiguous` (which blocks the phase) |
| Blockers go to the user mid-build | Blockers stop that phase and its dependents; everything else continues, and blockers come back in the result |
| Fix rounds continue the same worker (`SendMessage`) | Each fix round is a fresh agent given the full phase brief plus what's still open |
| Worktrees for parallel implementers | Shared tree with disjoint ownership. Merges need judgment the script can't exercise |
| You run git | One serialized "git operator" agent at a time, explicit paths only |
| Integration failures: you decide which side is wrong | Reported in the result; you resolve them after the run, in subagent mode |

Everything else is the same: spec-first tests committed before implementation, implementers who
can't edit tests, MUST-FIX and SHOULD-FIX both blocking, a cap of 3 fix rounds, regression with
in-flight files marked expected, the traceability check at review and final verification, and a
commit per verified phase.

Runtime limits: about `min(16, CPUs − 2)` agents run at once (the rest queue), a run is capped at
1,000 agents in total, and resume works only within the same Claude Code session.

## Before launch

1. Steps 1–2 of the main skill: read the blueprint, validate the manifest, pre-flight, baseline.
2. The permission choice from kickoff matters even more here. Workflow agents run in `acceptEdits`
   mode, so file edits don't prompt, but shell commands that aren't allowlisted will prompt mid-run
   and stall the workflow.
3. Write the initial progress file yourself. The script can't touch files.
4. Build `args` (below) and call **Workflow** with the script inline and `args` as real JSON (not a
   stringified blob). The user approves the launch card; the run proceeds in the background.

## Building args

Built from the manifest and the docs you read:

```js
{
  root: "/abs/project/root",
  skillDir: "/abs/path/to/claude-build",          // agents read their persona files from here
  planDoc: "docs/architecture/implementation-plan.md",   // the doc holding the Build Manifest
  mode: "PM",                                      // or "Developer"
  designSystem: "docs/design-system/design-system.md",   // or null
  conventions: [],                                 // Developer mode: conventions + testing-strategy paths
  archDocs: ["docs/architecture/overview.md", "docs/architecture/component-design.md"],
  commands: { test: "...", test_one: "... {files}", typecheck: "...", build: "...", smoke: "..." },
  models: {                                        // Model routing (main skill); change only if the user asked
    writer: "opus", writerHigh: "opus", impl: "sonnet", implHigh: "opus", review: "opus",
    skeptic: "sonnet", runner: "haiku", integration: "opus", docs: "sonnet"
  },
  phases: [{
    id: "p4b", name: "Invoices", kind: "logic", risk: "high", depends_on: ["p2", "p3"],
    owns: ["src/invoices/**"], tests: ["src/invoices/invoice.service.test.ts"], shared: [],
    refs: ["US-3", "AC-3.1", "BR-4"], testFocus: "...",
    requirementDocs: ["docs/requirements/billing.md"],
    interfaceDocs: ["docs/architecture/component-design.md#invoices"],
    archDocs: ["docs/architecture/data-model.md"],
    exemplars: ["src/accounts/account.service.ts"], testExemplars: ["src/accounts/account.service.test.ts"],
    ui: false, judgment: true,                     // your kickoff classification: judgment-heavy → implHigh
    checks: ""                                     // non-test kinds: the verification command(s)
  }],
  integration: [{ name: "backend-e2e", after: ["p4a", "p4b"], verifies: "...",
                  folder: "tests/integration/backend-e2e" }],
  docs: { prompt: "README setup/run/test, API reference for the invoice endpoints" }   // or null
}
```

For non-test kinds, set `checks` to the commands the kind calls for: build and smoke for
`scaffold`/`wiring`, typecheck for `contracts`, migrate up on an empty DB for `data`.

## The script

Adapt it rather than writing orchestration from scratch. It's plain JavaScript: no type
annotations, no `Date.now()`/`Math.random()`, and no file or shell access from the script itself
(only agents do I/O).

```js
export const meta = {
  name: 'claude-build',
  description: 'Build the approved architecture: spec-first tests, implementation, verified review, integration, docs, final verification',
  phases: [
    { title: 'Build', detail: 'each phase starts when its dependencies verify: tests → implement → review → fix → regression → commit' },
    { title: 'Integrate', detail: 'integration checkpoints and smoke' },
    { title: 'Document' },
    { title: 'Verify', detail: 'full test, typecheck, build, smoke' },
  ],
}

const A = args
const C = A.commands
const M = A.models
const PHASES = A.phases
const byId = Object.fromEntries(PHASES.map(p => [p.id, p]))
const status = {}                 // id -> { state: 'verified' | 'blocked' | 'skipped' | 'failed', ... }
const started = new Set()

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
    ruling: { type: 'string', enum: ['test-wrong', 'code-wrong', 'spec-ambiguous'] } } } } } }
const RUN = { type: 'object', required: ['passed'], properties: {
  passed: { type: 'boolean' }, total: { type: 'number' }, failed: { type: 'number' },
  unexpectedFailures: { type: 'array', items: { type: 'object', properties: { file: STR, test: STR, reason: STR } } },
  expectedFailures: LIST, unexpectedPasses: LIST, typecheck: STR, build: STR, smoke: STR } }
const GIT = { type: 'object', required: ['ok'], properties: { ok: { type: 'boolean' }, commit: STR, detail: STR } }

// ---------- shared prompt pieces
const persona = role => `First read and follow ${A.skillDir}/references/personas/${role}.md.`
const WORKER = `Project root: ${A.root}. You are not alone: other agents are editing other files right now — don't revert edits you didn't make. Don't run git commands that change state; a git operator handles git.`
const testOne = files => C.test_one.replace('{files}', files.join(' '))
const inFlight = except => PHASES
  .filter(p => started.has(p.id) && status[p.id]?.state !== 'verified' && p.id !== except)
  .flatMap(p => [...(p.tests || []), ...(p.owns || [])])
const verifiedTests = () => PHASES.filter(p => status[p.id]?.state === 'verified').flatMap(p => p.tests || [])

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
  'spec: every cited requirement is implemented and tested, nothing uncited is invented, and the test files are unchanged since their commit',
  'architecture: interfaces, data model, error handling and technical decisions match the architecture docs',
  'edge cases, error paths and security: boundaries, invalid input, authz gaps, injection, unsafe data handling',
]
async function review(ph, what, read, label) {
  const high = ph.risk === 'high' || ph.judgment
  const lenses = high ? LENSES : ['all of these — ' + LENSES.join('; ')]
  const panels = await parallel(lenses.map((lens, i) => () => agent(
    `${persona('reviewer')}\n${WORKER}\nReview ${what} for phase ${ph.id} "${ph.name}" through this lens: ${lens}.
Read: ${read}. Requirement refs: ${ph.refs.join(', ') || 'none'}.
Report MUST-FIX and SHOULD-FIX findings with file, line and evidence. Both block, so don't file taste preferences.`,
    { label: `${label}:L${i + 1}`, phase: 'Build', model: M.review, schema: FINDINGS })))
  const claims = panels.filter(Boolean).flatMap(p => [
    ...p.mustFix.map(f => ({ ...f, severity: 'MUST-FIX' })),
    ...p.shouldFix.map(f => ({ ...f, severity: 'SHOULD-FIX' }))])
  const votes = high ? 3 : 1
  const judged = await parallel(claims.map((f, i) => () =>
    parallel(Array.from({ length: votes }, (_, j) => () => agent(
      `A reviewer claims this ${f.severity} issue in phase "${ph.name}": ${f.title} — ${f.detail} (${f.file || 'n/a'}:${f.line || '?'}).
Read the cited code, and for context: ${read}. Try to refute it — is it wrong, already handled, or outside this phase? Answer real=true only if the code genuinely has this problem.`,
      { label: `${label}:check${i + 1}.${j + 1}`, phase: 'Build', model: M.skeptic, schema: VERDICT })))
      .then(vs => ({ f, real: vs.filter(Boolean).filter(v => v.real).length * 2 > votes }))))
  return judged.filter(Boolean).filter(j => j.real).map(j => j.f)
}

// ---------- one phase, end to end
async function buildPhase(ph) {
  started.add(ph.id)
  const testFirst = ph.kind === 'logic' || ph.kind === 'ui'
  const docs = `requirements ${ph.requirementDocs.join(', ')}; interfaces ${ph.interfaceDocs.join(', ')}` +
    (A.conventions.length ? `; conventions ${A.conventions.join(', ')}` : '')
  const stop = (state, reason, extra) => (status[ph.id] = { state, reason, ...(extra || {}) })

  // 1. spec-first tests, then lock them in a commit
  let testFiles = []
  if (testFirst) {
    const writerPrompt = `${persona('test-writer')}\n${WORKER}
Phase ${ph.id} "${ph.name}". Requirement refs: ${ph.refs.join(', ')}. Test focus: ${ph.testFocus}.
Read: ${docs}. Style references only: ${ph.testExemplars.join(', ')}.
You own ONLY: ${ph.tests.join(', ')}. Never open implementation files.
Run your tests with: ${testOne(ph.tests)} — they should fail. Report unexpected passes.
If a criterion is too ambiguous to test, set "blocked" to the question.`
    const t = await agent(writerPrompt, { label: `tests:${ph.id}`, phase: 'Build',
      model: ph.risk === 'high' ? M.writerHigh : M.writer, schema: TESTS })
    if (!t) return stop('failed', 'test-writer died')
    if (t.blocked) return stop('blocked', `spec question: ${t.blocked}`)
    testFiles = t.files
    await git(`git add ${testFiles.join(' ')} && git commit -m "test(${ph.id}): spec tests for ${ph.name} [${ph.refs.join(', ')}]"`, `git:tests:${ph.id}`, 'Build')

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

  // 2. implement, with the tests read-only
  const check = testFirst ? testOne(testFiles) : ph.checks
  const implPrompt = `${persona('implementer')}\n${WORKER}
Implement phase ${ph.id} "${ph.name}" (${ph.kind}). Requirement refs: ${ph.refs.join(', ') || 'none'}.
Read: architecture ${[...A.archDocs, ...ph.archDocs].join(', ')}; ${docs}; exemplars ${ph.exemplars.join(', ')}.
${testFirst ? `Make these tests pass. Read them; never edit, skip or weaken them: ${testFiles.join(', ')}.` : ''}
Verify with: ${check}.
Own (edit nothing else): ${ph.owns.join(', ')}${(ph.shared || []).length ? `; shared, you're its only writer now: ${ph.shared.join(', ')}` : ''}.
${ph.ui ? `Use the frontend-design skill.${A.designSystem ? ` Follow ${A.designSystem}.` : ''}` : ''}
If a test looks wrong, list it under disputes with the requirement text. If a rule you need is missing, set "blocked".`
  const implModel = ph.risk === 'high' || ph.judgment ? M.implHigh : M.impl
  let impl = await agent(implPrompt, { label: `impl:${ph.id}`, phase: 'Build', model: implModel, schema: IMPL })
  if (!impl) return stop('failed', 'implementer died')
  if (impl.blocked) return stop('blocked', `missing rule: ${impl.blocked}`)

  // 3. test disputes: a judge rules against the requirements
  if ((impl.disputes || []).length) {
    const r = await agent(`Rule on these disputes between the spec tests and the implementer for phase "${ph.name}": ${JSON.stringify(impl.disputes)}.
Read the tests, the cited requirement text in ${ph.requirementDocs.join(', ')}, and ${ph.interfaceDocs.join(', ')}. For each: test-wrong, code-wrong, or spec-ambiguous (the requirements genuinely don't settle it).`,
      { label: `judge:${ph.id}`, phase: 'Build', model: M.review, schema: RULINGS })
    const rulings = (r && r.rulings) || []
    const ambiguous = rulings.filter(x => x.ruling === 'spec-ambiguous')
    if (ambiguous.length) return stop('blocked', 'spec-ambiguous test disputes', { disputes: ambiguous })
    const wrongTests = rulings.filter(x => x.ruling === 'test-wrong')
    if (wrongTests.length) {
      await agent(`${persona('test-writer')}\n${WORKER}\nA judge ruled these tests wrong against the spec: ${JSON.stringify(wrongTests)}. Fix only those tests. Own only: ${ph.tests.join(', ')}.`,
        { label: `fix-tests:${ph.id}:ruling`, phase: 'Build', model: M.writerHigh, schema: TESTS })
      await git(`git add ${testFiles.join(' ')} && git commit -m "test(${ph.id}): correct tests per ruling"`, `git:ruling:${ph.id}`, 'Build')
    }
    impl = await agent(`${implPrompt}\n\nRulings on your disputes: ${JSON.stringify(rulings)}. Where the code was ruled wrong, change the code.`,
      { label: `impl:${ph.id}:after-ruling`, phase: 'Build', model: implModel, schema: IMPL }) || impl
  }

  // 4. run + review + fix, both severities, max 3 rounds
  const read = `the phase's changes (git diff -- ${ph.owns.join(' ')})${testFiles.length ? `, tests ${testFiles.join(', ')}` : ''}, ${docs}`
  let run = null
  let open = []
  for (let round = 0; round < 3; round++) {
    run = await agent(`${persona('test-runner')}\nRun: ${check}. Expected: all-pass.`,
      { label: `run:${ph.id}#${round}`, phase: 'Build', model: M.runner, schema: RUN })
    open = await review(ph, 'the implementation', `${read}. Also run python3 ${A.skillDir}/scripts/check_traceability.py ${A.planDoc} --root ${A.root} --phase ${ph.id} — a cited AC/BR no test mentions is a MUST-FIX`, `review:${ph.id}#${round}`)
    if (run && run.passed && !open.length) break
    if (round === 2) break
    // escalate on failure: the last fix round runs a tier up
    await agent(`${implPrompt}\n\nFix round ${round + 1}. Failing checks: ${JSON.stringify((run && run.unexpectedFailures) || [])}.
Verified findings — fix every one, MUST-FIX and SHOULD-FIX alike: ${JSON.stringify(open)}`,
      { label: `fix:${ph.id}#${round}`, phase: 'Build', model: round >= 1 ? M.implHigh : implModel, schema: IMPL })
  }
  if (!(run && run.passed) || open.length) return stop('blocked', 'still open after 3 rounds', { open, failures: run && run.unexpectedFailures })

  // 5. regression over everything verified so far, then commit
  const expected = inFlight(ph.id)
  let reg = await agent(`${persona('test-runner')}\nRun: ${testOne([...verifiedTests(), ...testFiles])}; then ${C.typecheck}.
Expected: all-pass, except failures confined to these in-flight files, which you list under expectedFailures: ${expected.join(', ') || 'none'}.`,
    { label: `regression:${ph.id}`, phase: 'Build', model: M.runner, schema: RUN })
  if (!(reg && reg.passed)) {
    await agent(`${implPrompt}\n\nRegression: earlier-phase checks now fail: ${JSON.stringify((reg && reg.unexpectedFailures) || [])}.
Fix it within your owned files. If the fix needs another phase's file, set "blocked" and explain.`,
      { label: `repair:${ph.id}`, phase: 'Build', model: implModel, schema: IMPL })
    reg = await agent(`${persona('test-runner')}\nRun: ${testOne([...verifiedTests(), ...testFiles])}; then ${C.typecheck}. Expected: all-pass except failures confined to: ${expected.join(', ') || 'none'}.`,
      { label: `regression:${ph.id}#2`, phase: 'Build', model: M.runner, schema: RUN })
    if (!(reg && reg.passed)) return stop('blocked', 'regression', { failures: reg && reg.unexpectedFailures })
  }
  const kindVerb = testFirst ? 'feat' : 'chore'
  const commit = await git(`git add ${[...ph.owns, ...(ph.shared || [])].join(' ')} && git commit -m "${kindVerb}(${ph.id}): ${ph.name} [${ph.refs.join(', ')}]"`, `git:phase:${ph.id}`, 'Build')
  return stop('verified', '', { commit: commit && commit.commit, tests: testFiles })
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

phase('Integrate')
const integration = await parallel((A.integration || []).map(cp => async () => {
  const notReady = cp.after.filter(d => status[d]?.state !== 'verified')
  if (notReady.length) return { name: cp.name, state: 'skipped', reason: `unverified: ${notReady.join(', ')}` }
  const res = await agent(`${persona('integration-tester')}\n${WORKER}
Checkpoint "${cp.name}" — prove: ${cp.verifies}. Read ${A.archDocs.join(', ')} and the implementation of phases ${cp.after.join(', ')}.
Write tests only under ${cp.folder}. Run them (${C.test_one.replace('{files}', cp.folder)}) and the smoke command (${C.smoke}); look at any screenshots under tmp/smoke/.`,
    { label: `integration:${cp.name}`, phase: 'Integrate', model: M.integration, schema: RUN })
  if (res && res.passed) await git(`git add ${cp.folder} && git commit -m "test(integration): ${cp.name}"`, `git:int:${cp.name}`, 'Integrate')
  return { name: cp.name, passed: !!(res && res.passed), failures: (res && res.unexpectedFailures) || [] }
}))

phase('Document')
if (A.docs) {
  await agent(`${persona('docs-writer')}\n${WORKER}\n${A.docs.prompt}\nDocument what was actually built. Don't change code behavior.`,
    { label: 'docs', phase: 'Document', model: M.docs })
  await git(`Stage only documentation files the docs writer changed (README, docs/, docstring-only changes) and commit with "docs: build documentation".`, 'git:docs', 'Document')
}

phase('Verify')
const integrationGlobs = (A.integration || []).map(cp => `"${cp.folder}/**"`).join(' ')
const final = await agent(`${persona('test-runner')}\nFinal verification, in order: ${C.test}; ${C.typecheck}; ${C.build}; ${C.smoke}; python3 ${A.skillDir}/scripts/check_traceability.py ${A.planDoc} --root ${A.root}${integrationGlobs ? ' --extra-tests ' + integrationGlobs : ''}. Expected: all-pass (the traceability check exits 0 when every cited requirement ID is proven by a test). Report typecheck, build, smoke and traceability status.`,
  { label: 'final-verification', phase: 'Verify', model: M.runner, schema: RUN })

return { status, integration, finalVerification: final,
  notVerified: blocked.map(([id, s]) => ({ id, ...s })) }
```

Notes:
- **Review scale** follows the main skill: one reviewer plus one skeptic per finding for normal
  phases, a three-lens panel plus three skeptics for `risk: high`. Scale up for security-sensitive
  builds by adding lenses or votes.
- **Scope = one phase or a subset:** pass only those phases in `args.phases` (and drop
  integration/docs as appropriate). Verified dependencies outside the subset must already be
  committed; leave them out of `depends_on`.
- **Iterate on the script:** edit the persisted file the Workflow tool returned and re-invoke with
  `{ scriptPath }`. **Resume after a stop** in the same session: `{ scriptPath, resumeFromRunId }`,
  so completed agents return cached results.

## After it returns

1. Read the result, then check it the way you'd check any report. Read the diff of every
   judgment-heavy and `risk: high` phase yourself — the lead review the script couldn't do mid-run —
   and spot-check a couple of others plus the test-lock (`git diff <test commit> -- <tests>`).
   Findings go to the owning implementer in subagent mode. Re-run final verification with a fresh
   runner if the result looks surprising.
2. Write the final progress file from the returned data.
3. Handle what's open in subagent mode: blocked phases go to the user with one AskUserQuestion card
   of options; integration failures go to the owning implementers; skipped phases resume once their
   dependencies are fixed.
4. Report as in step 7 of the main skill. Say plainly which parts the workflow verified and which
   are still open.
