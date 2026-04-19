---
name: agent-design
description: "Design AI agents from business problems and objectives. Produces complete agent architecture documents including system prompts, tool schemas, memory strategies, coordination patterns, and implementation specs targeting the Claude Agent SDK. Use this skill whenever the user wants to design an agent, plan an agent system, architect a multi-agent workflow, figure out how to structure an AI agent for a task, or asks questions like 'how should I build an agent for X'. Also trigger when the user mentions agent architecture, agent design patterns, or wants to go from a business problem to an agent implementation plan."
---

# Agent Design

Turn business problems into implementation-ready agent architectures targeting the Claude Agent SDK.

The goal is simple: when someone finishes reading your design document, building the agent should be purely an implementation problem. Every architectural decision is made, every prompt is written, every tool is defined, every edge case is handled. The builder's job is to translate your spec into code, not to make design choices.

## How This Skill Works

The design process has four phases:

1. **Understand** — Interview the user to grasp the business problem, constraints, and success criteria
2. **Architect** — Select the right agent pattern and explain why
3. **Specify** — Write the full design: system prompts, tools, memory, coordination, error handling
4. **Review** — Walk the user through the design and refine based on feedback

---

## Phase 1: Understand the Problem

Start by understanding what the agent needs to accomplish. Ask focused questions — you're trying to learn enough to make architectural decisions, not write a requirements document.

### What You Need to Know

**The core task**: What does the agent do? What's the input, what's the output? Walk through a concrete example end-to-end with the user.

**Users and environment**: Who triggers the agent — a human, a cron job, another system? What does the interaction look like? Is it conversational (back-and-forth) or fire-and-forget (input → output)?

**Data and systems**: What does the agent need access to? Files, APIs, databases, web? What are the read/write permissions? Are there authentication requirements?

**Constraints**: What are the hard limits? Latency budget, cost ceiling, security requirements, compliance rules, rate limits on external APIs.

**Success criteria**: How will the user know the agent is working well? What does a good output look like vs. a bad one? Are there measurable metrics?

**Failure modes that matter**: What happens when the agent gets it wrong? Is a bad answer worse than no answer? Are there actions that are hard to reverse?

### Interview Approach

Keep the interview to 2-3 rounds of questions. Batch related questions together. Use `AskUserQuestion` with predefined options when the answer space is bounded (e.g., interaction model, latency requirements). Use open-ended questions when you need the user to describe their domain.

After the interview, summarize your understanding back to the user before moving on. This is your last chance to catch misunderstandings before they propagate through the entire design.

---

## Phase 2: Architect — Select the Right Pattern

This is where you earn your keep. Based on what you learned in Phase 1, choose an agent architecture pattern and explain your reasoning to the user.

Read `references/agent-patterns.md` for the full pattern catalog. The key decision points are:

### Single Agent vs. Multi-Agent

Start with the simplest thing that could work. A single agent with good tools handles more than people expect. You need multiple agents when:

- **The task has distinct phases** that benefit from different system prompts (e.g., research → analysis → writing). A single prompt trying to be good at everything often ends up mediocre at each.
- **Subtasks are independent** and can run in parallel. If you're reviewing 5 files, 5 parallel agents finish faster than 1 sequential agent.
- **Information isolation matters**. Sometimes agents do better work when they *don't* see everything — a test writer who can't see the implementation writes better tests.
- **The context window is a real constraint**. If the task requires holding more information than fits in one context window, splitting across agents is the way.

If none of these apply, use a single agent. Don't add complexity for its own sake — every additional agent adds latency, cost, and coordination overhead.

### Pattern Selection

Once you've decided on the general shape, select a specific pattern from the catalog. Present your recommendation to the user with:

1. **The pattern you chose** and a one-paragraph description
2. **Why this pattern fits** — connect it back to their specific problem
3. **What you considered and rejected** — briefly, so they understand the tradeoff
4. **A visual sketch** of the architecture (agents, tools, data flow) using a simple text diagram

Wait for the user to confirm before proceeding to the detailed design.

---

## Phase 3: Specify — The Design Document

This is the bulk of the output. Write everything needed so that building the agent is just an implementation exercise.

### Document Structure

Write the design to `docs/agent-design.md` (or a directory of files for complex multi-agent systems). The document follows this structure:

```
# [Agent Name] — Design Specification

## Overview
- What the agent does (one paragraph)
- Architecture pattern and rationale
- Architecture diagram (text-based)

## Agent Definitions
  (for each agent in the system)
  ### [Agent Name / Role]
  - Role and responsibilities
  - System prompt (complete, ready to use)
  - Tools (with full MCP schemas)
  - Memory strategy
  - Input/output contract

## Coordination
  (multi-agent only)
  - Communication patterns
  - Task delegation logic
  - Shared state management

## Error Handling & Recovery

## Human-in-the-Loop Checkpoints

## Evaluation Strategy

## Implementation Guide
  - File structure
  - SDK integration
  - Configuration
  - Dependencies
```

### Writing Agent Definitions

For each agent (or the single agent), specify:

#### Role & Responsibilities
A clear statement of what this agent does and — just as importantly — what it does *not* do. Boundaries prevent scope creep during implementation.

#### System Prompt

Write the complete system prompt. This is the most important part of the design. A few principles:

- **Lead with identity and purpose.** The first 2-3 sentences should tell the agent who it is and what it's trying to accomplish. This anchors everything that follows.
- **Explain the why.** Don't just say "always validate inputs" — explain that invalid inputs cause downstream failures that are hard to debug. Models with good theory of mind respond better to reasoning than rules.
- **Be specific about output format.** If you want JSON, show the exact schema. If you want markdown, show the template. Ambiguity in output format is the #1 source of agent reliability issues.
- **Include examples for tricky cases.** One good example is worth ten sentences of explanation. Use the `Example 1: / Input: / Output:` pattern.
- **Describe failure modes and what to do.** "If you can't find the file, ask the user for the correct path. Don't guess." This prevents the agent from improvising in ways that cause damage.
- **Keep it under ~800 words.** Longer prompts don't mean better agents. If you're past 800 words, you're probably trying to make one agent do too many things — consider splitting into multiple agents.

#### Tools

For each tool the agent needs, provide the complete MCP tool definition:

```json
{
  "name": "tool_name",
  "description": "What this tool does and when to use it",
  "inputSchema": {
    "type": "object",
    "properties": { ... },
    "required": [ ... ]
  }
}
```

Tool design principles:
- **Name tools as verb-noun pairs**: `search_documents`, `create_ticket`, `validate_schema`. The model reads tool names as action descriptions.
- **Write descriptions for the model, not humans.** The description tells the model *when* and *why* to use the tool, not just what it does. "Search the knowledge base for articles matching a user question. Use this before attempting to answer questions about product features." is better than "Searches articles."
- **Constrain the input schema.** Use enums for bounded choices, set maxLength on strings, mark required fields. The tighter the schema, the fewer malformed calls.
- **Include an `annotations` field** where relevant: `readOnlyHint`, `destructiveHint`, `openWorldHint`. These help the SDK's permission system and communicate intent.

Also specify which built-in SDK tools the agent needs access to (Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch) and any that should be explicitly disallowed.

#### Memory Strategy

Define what the agent needs to remember and how:

- **Within a conversation**: What goes in the system prompt vs. retrieved on demand? Does the agent need to track state across turns?
- **Across conversations** (if applicable): What should persist? Use the SDK's session mechanism, files on disk, or an external store?
- **Context window management**: For long-running agents, how should context be managed? What can be safely compacted? What must stay in the window?

#### Input / Output Contract

Define the exact interface:
- What the agent receives (format, required fields, optional fields)
- What the agent produces (format, structure, where it's written)
- For sub-agents: how the parent passes work in and how results come back

### Coordination (Multi-Agent Systems)

For multi-agent designs, specify:

**Communication pattern**: How do agents talk to each other?
- Direct delegation (orchestrator spawns sub-agents with task descriptions)
- Shared task list (agents claim and complete tasks)
- Mailbox messaging (peer-to-peer messages between agents)
- Pipeline (output of one agent is input to the next)

**Task delegation logic**: How does the orchestrator decide what to delegate and to whom? Write this as concrete rules, not vague guidelines.

**Shared state**: What state is shared between agents? Where does it live (files on disk, a status document, a task list)? Who can read and write it?

**Concurrency limits**: How many agents can run in parallel? This affects both cost and coordination complexity. Recommend specific limits based on the task.

**Synchronization points**: Where do agents need to wait for each other? What happens at each checkpoint?

### Error Handling & Recovery

Agents fail differently than traditional software. Design for these failure modes:

- **Hallucination**: The agent fabricates information. Mitigate with tool-based verification, grounding instructions, and confidence thresholds.
- **Infinite loops**: The agent retries the same failing action. Set maximum iteration counts for all retry loops (usually 3).
- **Tool misuse**: The agent calls tools with wrong arguments or at wrong times. Tight schemas and clear descriptions reduce this; validation in tool handlers catches the rest.
- **Context overflow**: The task requires more context than fits in the window. Plan for context management — what to keep, what to summarize, what to offload to files.
- **Partial failure in multi-agent systems**: One sub-agent fails while others succeed. Define fallback behavior — retry, skip, escalate to user.

For each failure mode relevant to this agent, specify: detection method, recovery action, and escalation path.

### Human-in-the-Loop Checkpoints

Identify points where the agent should pause and get human confirmation:

- **Irreversible actions**: Deleting data, sending emails, making API calls with side effects
- **High-stakes decisions**: Actions with significant cost or business impact
- **Ambiguous situations**: When the agent isn't confident about the right path
- **Quality gates**: Review points before proceeding to the next phase

For each checkpoint, specify what information to present to the user and what options they should have (approve, modify, reject, provide input).

### Evaluation Strategy

Define how to know the agent is working:

- **Functional tests**: Specific input → expected output pairs that can be run automatically
- **Quality metrics**: Measurable indicators of output quality (accuracy, completeness, format compliance)
- **Edge case tests**: Inputs designed to probe failure modes (malformed input, missing data, ambiguous requests)
- **Human evaluation criteria**: What a human reviewer should look for that can't be automated

### Implementation Guide

Bridge the design to code:

**File structure**: Show the complete project layout with file purposes.

**SDK integration points**: Map each design element to Claude Agent SDK concepts:
- Agent definitions → `query()` calls with system prompts and tool configurations
- Custom tools → MCP server tool definitions with handlers
- Multi-agent coordination → subagent spawning with `Agent` tool
- Memory → sessions, file-based persistence, or external stores
- Permissions → `allowed_tools` / `disallowed_tools` configuration
- Hooks → lifecycle event handlers for logging, validation, etc.

**Configuration**: Environment variables, API keys, feature flags, tunable parameters.

**Dependencies**: External packages, MCP servers, API access needed.

---

## Phase 4: Review

After writing the design document:

1. Present a summary of key decisions and their rationale
2. Walk through any areas where you made judgment calls
3. Ask the user to review, offering these options:
   - **Looks good** — design is ready for implementation
   - **Minor adjustments** — specific things to change
   - **Rethink an area** — revisit a particular section
   - **Different pattern** — reconsider the architecture

Iterate until the user is satisfied. The design should feel complete enough that they could hand it to a developer (or an agent team) and get back a working system.

---

## Reference Files

- `references/agent-patterns.md` — Full catalog of agent architecture patterns with decision criteria, diagrams, and tradeoff analysis. Read this during Phase 2 to select the right pattern.
- `references/sdk-reference.md` — Claude Agent SDK capabilities, code examples, and implementation patterns. Read this during Phase 3 when writing the implementation guide.
