# AI / agent features in the requirements

Read this when the requirements describe an AI agent, LLM-powered feature, chatbot, RAG system, classification/extraction agent, or anything similar — or when you find an existing `agent-design/` directory in the project.

## Division of labor

The details of the agent — data sources, tools, prompts, output formats, model choice, eval plan — belong to the **`agent-design`** skill, not to you. Your job is to design the *surrounding system*:

- where the agent lives in the file structure
- what interface it exposes (input type, output type, error surface)
- which component calls it and how its output is consumed
- what infrastructure it needs (vector store, background queue, logging/tracing, secrets management)
- auth / rate-limit patterns around it
- which implementation phase it fits into (after the infra it depends on)

**Do NOT write prompts, tool schemas, or model choices into your architecture docs.** Keep your docs at the architectural level — where the agent lives, what it exposes, what it depends on.

## If `agent-design/` already exists

Look for `/docs/features/{feature-name}/agent-design/`, `/docs/agent-design/`, or `./agent-design/`. If one exists, the `agent-design` skill has already run and **its outputs are fixed inputs to you, not things you redesign.** Read the folder — especially `overview.md`, `integration.md`, `agents.md`, and `orchestration.md` if present — to understand: what the agent(s) do, the model/runtime shape chosen, the invocation signature the agent exposes, and any infra dependencies implied (vector store, queue, background worker). Treat these as non-negotiable constraints, then run the **thin pass** below.

## Deciding when `agent-design` runs

If there's no existing `agent-design/` directory, use AskUserQuestion once to decide its timing relative to your architecture:

```
AskUserQuestion({
  questions: [{
    question: "The requirements describe an AI agent. How central is it to the product?",
    header: "Agent role",
    multiSelect: false,
    options: [
      { label: "Feature within the app (Recommended)", description: "The app has a broader architecture; the agent is one component. I'll design the surrounding system with the agent as a placeholder interface, then you run `agent-design` afterward to fill in prompts/tools/data." },
      { label: "The agent IS the product", description: "The app is primarily a thin wrapper around the agent. Run `agent-design` first so its outputs (model, data, tools, orchestration) drive my architecture decisions — I'll pause here." },
      { label: "Too small to matter", description: "A trivial LLM call (e.g., a one-shot summarization). I'll design it inline without running `agent-design`." }
    ]
  }]
})
```

- **Feature within the app (most common):** Design the architecture normally. In the file structure, allocate a clear home for the agent (e.g., `src/agents/triage/`) and specify its interface — input type, output type, error surface — as a component in `component-design.md`. Leave the agent's internals (prompts, tool implementations, model choice) unspecified, but mark that section: "Agent internals are specified by `agent-design/`. Run the `agent-design` skill after this architecture is approved, before handing off to `dev-team`." In the implementation phasing, place the agent's phase after the infrastructure it depends on (data model, APIs it consumes). `dev-team` will pick up both your docs and `agent-design/` when implementing.
- **The agent IS the product:** Stop and tell the user to run `agent-design` first. Write a minimal architecture scaffold (tech stack + "thin API around the agent") only if the user wants something now; otherwise wait for `agent-design/` to complete, then design the wrapping system around its decisions (the agent-design's model, data sources, and orchestration pattern become non-negotiable constraints on your architecture).
- **Too small to matter:** Design the feature inline. You can still specify a simple system prompt and the call shape in your design, but don't pretend it's a full agent — it's a single LLM call.

## The thin pass (invoked after `agent-design`)

If you detected an existing `agent-design/` directory in "Before You Start", the agent has already been designed in detail — your job is narrow. `dev-team` needs stack + file structure + phases to execute, and `agent-design` intentionally doesn't produce those. Scope your pass to exactly these decisions:

1. **Language + runtime.** Python vs. TypeScript (or both, if agent + wrapper differ). Runtime shape: CLI, HTTP server (FastAPI / Next.js API route / Express), queue consumer, serverless function, long-running worker. Base this on `integration.md`'s invocation signature and any runtime hints in `overview.md`.
2. **File structure.** Where the agent lives on disk, where tool implementations live, where prompts live (imported from code, or loaded from `prompts.md` at runtime?), where the eval harness lives. Produce an ownership map just like a normal architecture pass.
3. **Test framework + eval harness shape.** Pick the framework. For the eval harness, turn `agent-design/evaluation.md`'s golden cases into a concrete harness shape (test runner, fixture format, how LLM-as-judge runs if used).
4. **Infra dependencies.** Surface anything the agent-design implies: vector store (if RAG), background queue (if async), observability stack (if tracing), secrets management (for API keys). Pick from the tiered ladder below based on the Phase 1 budget tier — *do not* default to the most capable option.
5. **Implementation phases.** Break the build into phases `dev-team` can execute. Typical shape for an agent build: scaffolding → tool implementations → agent loop wiring → eval harness → integration/observability. Adapt based on what `agent-design` calls for.

Skip the parts of a normal architecture pass that don't apply — no data model design (the agent's data sources are already specified), no API design unless there's a wrapper API, no UI unless there's one. Use AskUserQuestion normally for the decisions above; keep total rounds down since the agent internals are already decided. Reference the `agent-design/` directory path in your docs' Requirements Reference section so `dev-team` knows to load both.

## Agent infra ladder (cost-aware)

Agent features have a reputation for racking up infra bills — vector DBs, managed queues, observability vendors, LLM API costs — and it's easy to recommend the "real" version of each piece without thinking about whether the project can afford it. Don't. Re-read the **budget tier** the user picked in Phase 1 (hobby / startup / scaling / enterprise) and use the ladder below to pick the right rung for *that tier*, not the rung you'd pick for a Fortune-500 client.

For each piece of infra below, the cheapest viable option on the left is genuinely fine for the cases described — many real production agent systems run on pgvector and stdout logs for years. Step right only when a requirement actually demands it.

| Concern | Cheapest viable (hobby / startup) | Typical (startup / scaling) | Enterprise |
|---|---|---|---|
| **Vector store** | `pgvector` on existing Postgres, or `sqlite-vss`. Free, no new service to operate. Fine up to ~1M vectors. | Pinecone starter, Weaviate Cloud, Qdrant Cloud entry tier. ~$70–$200/mo. | Self-hosted Weaviate/Qdrant cluster, or Pinecone production tier, with replication and SLA. |
| **Background queue** | In-process worker (BullMQ, Sidekiq, Celery on the same node), or `pg-boss` (DB-backed). Free. Fits low-volume async work. | Managed Redis (Upstash, Redis Cloud) with a dedicated worker, or SQS / Cloud Tasks. $20–$100/mo. | Managed Kafka, EventBridge, or a self-hosted event bus. Justified only when you need durable event streams, replay, or cross-service fan-out. |
| **Observability / tracing** | Structured JSON logs to stdout, captured by the platform's built-in log viewer. Free. | Logflare, Axiom, Better Stack, or a single Honeycomb starter env. $0–$50/mo. | Datadog APM, Honeycomb production, or New Relic full stack with traces, profiling, and alerts. |
| **Secrets / API keys** | Env vars from the host or platform's built-in secret store (Render/Fly/Vercel secrets). Free. | AWS Parameter Store, GCP Secret Manager, Doppler. $0–$10/mo. | AWS Secrets Manager with rotation, HashiCorp Vault, or a compliance-scoped KMS-backed store. |
| **LLM API spend** | Smaller / cheaper models for non-critical paths (Haiku, GPT-4o-mini, Gemini Flash); cache aggressive; batch where possible. | Mid-tier models for primary paths, smaller models for cheap sub-tasks; observability on token spend. | Top-tier models everywhere it helps; reserved capacity / committed-spend deals; per-feature cost dashboards. |

**On hobby / startup tiers, "not having it" is also a valid answer.** If the project doesn't *need* a vector store yet (small corpus, or no RAG yet), defer it. If async isn't required, skip the queue entirely and run inline. If there's no production traffic yet, observability beyond stdout is premature. Surfacing the option to defer is part of right-sizing.

When you write up the Deployment & Infrastructure sub-section for an agent-heavy build, name the rung you picked for each row of the ladder and state the budget reason (e.g., "Vector store: pgvector on the existing Postgres instance — startup tier, ~50k vectors at launch, can move to Pinecone if we cross 500k or need filtering at scale.").

Mode still applies on a thin pass — see `developer-mode.md` for what a Developer-mode thin pass adds.
