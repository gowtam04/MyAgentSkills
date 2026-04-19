# Agent Architecture Patterns

A catalog of agent architecture patterns for the Claude Agent SDK. Use this during Phase 2 (Architect) to select the right pattern for the problem at hand.

## Table of Contents
1. [Single Agent](#single-agent)
2. [Orchestrator-Workers](#orchestrator-workers)
3. [Pipeline](#pipeline)
4. [Parallel Specialists](#parallel-specialists)
5. [Evaluator-Optimizer](#evaluator-optimizer)
6. [Router](#router)
7. [Decision Matrix](#decision-matrix)

---

## Single Agent

**One agent with a focused system prompt and a well-chosen set of tools.**

```
User → [Agent + Tools] → Output
```

### When to Use
- The task has a clear, bounded scope
- All required context fits in one context window
- The workflow is mostly linear (do A, then B, then C)
- Low latency is important — no coordination overhead

### When to Avoid
- The task requires fundamentally different "modes of thinking" (e.g., creative generation followed by rigorous validation)
- Subtasks are independent and parallelizable
- The context window is a bottleneck

### Design Tips
- Put effort into the system prompt and tool selection — a well-prompted single agent with good tools beats a poorly designed multi-agent system
- Use the agent's tool set as guardrails: if it shouldn't write to the database, don't give it a database write tool
- Keep the system prompt focused. If you're writing "when doing X... but when doing Y..." the agent might be trying to do too much

### Example Use Cases
- Code review agent that reads files, analyzes patterns, and writes a review
- Customer support agent that queries a knowledge base and responds to tickets
- Data extraction agent that reads documents and outputs structured data

---

## Orchestrator-Workers

**A central orchestrator agent that breaks down complex tasks and delegates to specialized worker agents.**

```
User → [Orchestrator]
            ├→ [Worker A + Tools] → result
            ├→ [Worker B + Tools] → result
            └→ [Worker C + Tools] → result
       [Orchestrator synthesizes] → Output
```

### When to Use
- The task naturally decomposes into distinct subtasks
- Different subtasks benefit from different system prompts, tools, or expertise
- You want information isolation (workers shouldn't see each other's context)
- The orchestrator needs to make dynamic decisions about what to delegate

### When to Avoid
- The decomposition is always the same (use Pipeline instead)
- You only need parallelism without intelligent coordination (use Parallel Specialists)
- The task is simple enough for a single agent

### Design Tips
- The orchestrator's system prompt should focus on *planning and delegation*, not doing the work itself. Its job is to break down the task, assign it, and synthesize results
- Give each worker a narrow, well-defined role. The prompt "You are a security reviewer. Analyze this code for vulnerabilities." works better than "You are part of a review team. Your focus area is security."
- Define clear input/output contracts between the orchestrator and workers — the orchestrator needs to know exactly what to send and what to expect back
- Set concurrency limits (3-5 workers is usually the sweet spot). More than that and coordination overhead dominates
- Build in a synthesis step where the orchestrator reviews worker outputs before presenting to the user

### Coordination Patterns
- **Spawn and wait**: Orchestrator spawns all workers, waits for all to complete, then synthesizes. Simplest to implement.
- **Progressive delegation**: Orchestrator spawns workers one at a time based on results from previous workers. More adaptive but slower.
- **Shared task list**: Workers pull from a shared list, allowing dynamic load balancing. Most flexible but most complex.

### Example Use Cases
- Research agent that delegates to search, analysis, and writing specialists
- Code migration agent that delegates file-by-file transformations to workers
- Report generator that delegates data collection, analysis, and formatting to specialists

---

## Pipeline

**A linear chain of agents where each agent's output becomes the next agent's input.**

```
User → [Agent A] → intermediate → [Agent B] → intermediate → [Agent C] → Output
```

### When to Use
- The task has clear sequential stages
- Each stage has a fundamentally different job (e.g., extract → transform → validate)
- The output format changes between stages
- You want each stage to be independently testable and replaceable

### When to Avoid
- Stages need to communicate back (pipeline only flows forward)
- The number or order of stages varies by input (use Orchestrator-Workers)
- Latency is critical — every stage adds a full agent round trip

### Design Tips
- Define the intermediate format between each stage explicitly. This is the "API" between pipeline stages — if it's ambiguous, the pipeline breaks
- Each agent should have no knowledge of the other agents in the pipeline. It receives an input, does its job, and produces an output
- Add validation between stages: a lightweight check that the output of stage N matches what stage N+1 expects
- Consider whether some stages can be simple code instead of agents. Not every transformation needs an LLM

### Example Use Cases
- Document processing: extract text → structure data → validate → generate report
- Content creation: research → outline → draft → edit → format
- Data pipeline: collect raw data → clean/normalize → analyze → visualize

---

## Parallel Specialists

**Multiple independent agents process different aspects of the same input simultaneously, with results merged at the end.**

```
User → [Input distributed]
            ├→ [Specialist A] → result A
            ├→ [Specialist B] → result B
            └→ [Specialist C] → result C
       [Results merged] → Output
```

### When to Use
- The same input needs to be analyzed from multiple independent perspectives
- Results can be meaningfully combined without complex negotiation
- Speed matters — parallelism directly reduces wall-clock time
- Each specialist's work doesn't depend on the others

### When to Avoid
- Specialists need to see each other's work (use Orchestrator-Workers)
- The results require intelligent synthesis, not just merging (use Orchestrator-Workers)
- There are only 1-2 perspectives needed (overhead of parallelism isn't worth it)

### Design Tips
- The merge step is the critical design point. For simple cases, concatenation works. For conflicting results, you need a resolution strategy (majority vote, priority ranking, or a synthesis agent)
- Give each specialist a distinct system prompt focused on their perspective. "Review for security" and "Review for performance" as separate agents outperform "Review for security and performance" as one agent
- This pattern combines well with a final synthesis agent that reads all specialist outputs and produces a unified result

### Example Use Cases
- Code review with parallel reviewers for security, performance, style, and correctness
- Document analysis from legal, financial, and technical perspectives
- Multi-criteria evaluation (score on accuracy, completeness, clarity independently)

---

## Evaluator-Optimizer

**A generator agent produces output, an evaluator agent critiques it, and the generator revises. The loop continues until quality criteria are met or a maximum iteration count is reached.**

```
User → [Generator] → draft
            ↓
       [Evaluator] → feedback
            ↓
       [Generator] → revised draft
            ↓
       [Evaluator] → approved ✓ → Output
```

### When to Use
- Output quality is critical and hard to get right in one pass
- You can define clear evaluation criteria
- The task benefits from iterative refinement (writing, code generation, design)
- You want to separate "creative generation" from "critical evaluation"

### When to Avoid
- The task is straightforward and usually right on the first attempt
- Speed is more important than quality
- Evaluation criteria are subjective and hard to articulate (the evaluator won't know what to look for either)

### Design Tips
- The evaluator's system prompt is more important than the generator's. A mediocre generator with a great evaluator converges on good output; a great generator with a mediocre evaluator wastes cycles
- Always set a maximum iteration count (usually 2-3). If it's not good after 3 rounds, the problem is in the prompts or tools, not the iteration count
- The evaluator should provide *actionable* feedback, not just scores. "The introduction is too vague — add specific metrics from Q3" beats "Quality: 6/10"
- Consider using different models for generator vs. evaluator if cost is a concern. A cheaper model can often evaluate what a more expensive model generates

### Example Use Cases
- Content writing with editorial review
- Code generation with test-based validation
- Data analysis with accuracy verification
- Proposal writing with criteria-based scoring

---

## Router

**A classifier agent examines the input and routes it to the appropriate specialist agent.**

```
User → [Router]
            ├→ if type A → [Agent A] → Output
            ├→ if type B → [Agent B] → Output
            └→ if type C → [Agent C] → Output
```

### When to Use
- Inputs are heterogeneous and need fundamentally different handling
- Each input type has a specialized workflow
- You want to keep each specialist's prompt focused and manageable
- The routing decision is clear-cut based on input characteristics

### When to Avoid
- Most inputs need the same handling (just use a single agent)
- Inputs often span multiple categories (routing becomes ambiguous)
- The routing logic is simple enough to handle in a single prompt with conditional behavior

### Design Tips
- The router should be fast and cheap — a short prompt that classifies and forwards. Don't give it tools or let it do actual work
- Define clear routing criteria and handle the "none of the above" case (fallback to a general-purpose agent or ask the user for clarification)
- Consider whether routing can be done with simple rules (keyword matching, file type detection) instead of an LLM. Code-based routing is faster and more predictable
- Each specialist should be self-contained — it receives the original input plus the routing context, and produces the final output

### Example Use Cases
- Customer support: route by issue type (billing, technical, account) to specialized agents
- Document processing: route by file type (PDF, spreadsheet, email) to extraction specialists
- Task automation: route by request type (create, update, delete, query) to CRUD specialists

---

## Decision Matrix

Use this matrix to guide pattern selection. Score each dimension for the problem at hand, then see which pattern fits best.

| Dimension | Single Agent | Orchestrator-Workers | Pipeline | Parallel Specialists | Evaluator-Optimizer | Router |
|---|---|---|---|---|---|---|
| **Task complexity** | Low-Medium | High | Medium-High | Medium | Medium-High | Varies |
| **Subtask independence** | N/A | Medium-High | Low (sequential) | Very High | Low (iterative) | Very High |
| **Need for iteration** | Low | Low | Low | Low | High | Low |
| **Latency sensitivity** | Best | Medium | Worst | Good | Medium | Good |
| **Cost sensitivity** | Best | Medium-High | Medium | Medium-High | High | Low-Medium |
| **Quality criticality** | Medium | High | High | High | Highest | Medium |
| **Input heterogeneity** | Low | Medium | Low | Low | Low | High |

### Combining Patterns

Patterns compose. Common combinations:

- **Router + Specialists**: Route inputs to specialist agents, each of which is a single agent or a mini-pipeline
- **Orchestrator + Evaluator**: Orchestrator delegates work, then runs an evaluator pass on the combined output
- **Pipeline + Parallel**: Pipeline stages where some stages parallelize internally (e.g., parallel analysis → sequential synthesis)
- **Orchestrator + Pipeline Workers**: Orchestrator spawns workers that each run a mini-pipeline

When combining patterns, be mindful of total system complexity. Each layer of nesting adds latency, cost, and debugging difficulty. Start with the simplest combination that handles the problem.
