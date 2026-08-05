# AI / agent features in the requirements

Read this when the requirements describe an AI agent, LLM-powered feature, chatbot, RAG system, classification/extraction agent, or anything similar.

## Design AI features as part of the architecture

Design the agent (or LLM feature) **as part of the normal architecture** — not via a separate skill or deferred doc set. Include:

- where the agent lives in the file structure
- what interface it exposes (input type, output type, error surface)
- which component calls it and how its output is consumed
- what infrastructure it needs (vector store, background queue, logging/tracing, secrets management)
- auth / rate-limit patterns around it
- which implementation phase it fits into (after the infra it depends on)

For **non-trivial agents**, also specify at the level builders need:

- model choice and runtime shape
- tools / data sources and their schemas
- prompt and output shape (system prompt outline, structured output if any)
- eval / golden-case plan under testing strategy

For a **trivial one-shot LLM call** (e.g. summarization), a simple call shape and system prompt inline is enough — don't over-structure it as a full agent system.

## Right-sizing depth

Use AskUserQuestion only if the agent's centrality changes structural choices (e.g. the product is mostly a thin wrapper around an agent vs. one feature among many). Otherwise design it like any other complex component: allocate a home in the file structure, define the interface, phase it after its dependencies, and put enough prompt/tool/eval detail in the architecture that implementers are not improvising.

Typical agent-heavy phasing: scaffolding → tool implementations → agent loop / model wiring → eval harness → integration / observability. Adapt to what the requirements call for.

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
