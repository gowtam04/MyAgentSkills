# Claude Agent SDK Reference

Quick reference for mapping agent designs to Claude Agent SDK implementation. Use this during Phase 3 (Specify) and Phase 4 (Review) when writing the implementation guide.

## Table of Contents
1. [Core Agent Loop](#core-agent-loop)
2. [System Prompts](#system-prompts)
3. [Custom Tools via MCP](#custom-tools-via-mcp)
4. [Built-in Tools](#built-in-tools)
5. [Subagents (Multi-Agent)](#subagents)
6. [Sessions & Memory](#sessions--memory)
7. [Permissions & Safety](#permissions--safety)
8. [Hooks](#hooks)
9. [Implementation Templates](#implementation-templates)

---

## Core Agent Loop

The SDK runs an agentic loop: Claude thinks, calls tools, observes results, and decides next steps.

### Python
```python
from claude_agent_sdk import query, Message

async for message in query(
    prompt="Your task here",
    system_prompt="Agent system prompt",
    tools=["Read", "Write", "Bash"],  # built-in tools
    mcp_servers=[my_custom_server],    # custom tools
    allowed_tools=["Read", "my_tool"], # pre-approved tools
    model="claude-sonnet-4-6",
):
    if message.type == "text":
        print(message.content)
    elif message.type == "tool_use":
        print(f"Calling {message.tool_name}")
```

### TypeScript
```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Your task here",
  systemPrompt: "Agent system prompt",
  tools: ["Read", "Write", "Bash"],
  mcpServers: [myCustomServer],
  allowedTools: ["Read", "my_tool"],
  model: "claude-sonnet-4-6",
})) {
  // handle messages
}
```

### Key Parameters
- `prompt` — The user's task (what to do)
- `system_prompt` — The agent's identity and instructions (who you are, how to behave)
- `tools` — Which built-in tools to expose
- `mcp_servers` — Custom tool servers
- `allowed_tools` — Tools that don't require user approval
- `disallowed_tools` — Tools explicitly blocked
- `model` — Which Claude model to use
- `max_turns` — Maximum agentic loop iterations (safety limit)

---

## System Prompts

The system prompt defines the agent's behavior. In the SDK, it's passed via `system_prompt`.

### Best Practices for Agent System Prompts

**Structure:**
```
[Identity — who you are, what you do]
[Context — the environment you operate in]
[Core instructions — how to approach the task]
[Tools guidance — when and how to use your tools]
[Output format — what to produce]
[Constraints — what NOT to do]
[Examples — concrete input/output pairs for tricky cases]
```

**Keep prompts focused.** A single-purpose agent with a 300-word prompt outperforms a multi-purpose agent with a 2000-word prompt. If the prompt is getting long, split into multiple agents.

**Use the system prompt for stable instructions** and the user prompt for per-task input. Don't put task-specific details in the system prompt.

---

## Custom Tools via MCP

Define domain-specific tools using in-process MCP (Model Context Protocol) servers.

### Python
```python
from claude_agent_sdk import MCPServer, Tool

server = MCPServer("my-tools")

@server.tool(
    name="search_knowledge_base",
    description="Search internal docs for answers to user questions. Use before answering product questions.",
    input_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "max_results": {"type": "integer", "default": 5, "maximum": 20}
        },
        "required": ["query"]
    },
    annotations={
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
async def search_knowledge_base(query: str, max_results: int = 5):
    results = await kb_client.search(query, limit=max_results)
    return [{"type": "text", "text": format_results(results)}]
```

### TypeScript
```typescript
import { MCPServer } from "@anthropic-ai/claude-agent-sdk";

const server = new MCPServer("my-tools");

server.tool({
  name: "search_knowledge_base",
  description: "Search internal docs for answers to user questions.",
  inputSchema: {
    type: "object",
    properties: {
      query: { type: "string", description: "Search query" },
      maxResults: { type: "integer", default: 5, maximum: 20 },
    },
    required: ["query"],
  },
  annotations: { readOnlyHint: true, openWorldHint: false },
  handler: async ({ query, maxResults }) => {
    const results = await kbClient.search(query, maxResults);
    return [{ type: "text", text: formatResults(results) }];
  },
});
```

### Tool Design Principles

**Naming**: Use `verb_noun` format. The model reads tool names as action descriptions:
- `search_documents` (clear) vs. `docSearch` (ambiguous)
- `create_ticket` (clear) vs. `ticket` (is this create? read? update?)

**Descriptions**: Write for the model. Include *when* to use, not just *what* it does:
- "Search the knowledge base for articles. Use this BEFORE attempting to answer questions about product features or pricing." (tells model the trigger)
- vs. "Searches the knowledge base." (model has to guess when to use it)

**Input schemas**: Constrain aggressively:
- Use `enum` for bounded choices
- Set `maxLength` on strings
- Mark `required` fields
- Add `description` to every property
- Use `default` values where sensible

**Return values**: Can be text, images (base64), or resource blocks. For complex outputs, return structured text (JSON or formatted markdown) that the model can parse.

**Error handling**: Return error messages as text content with `is_error: true`. This keeps the agent loop alive — the model can retry or try a different approach:
```python
return [{"type": "text", "text": f"Error: {str(e)}"}], True  # is_error=True
```

**Annotations** guide the permission system:
- `readOnlyHint: true` — Tool only reads data, never modifies
- `destructiveHint: true` — Tool performs irreversible actions
- `idempotentHint: true` — Safe to retry without side effects
- `openWorldHint: true` — Tool interacts with external systems

---

## Built-in Tools

The SDK provides these tools out of the box:

| Tool | Purpose | When to Include |
|------|---------|-----------------|
| `Read` | Read files from disk | Any agent that needs file access |
| `Write` | Create new files | Agents that produce file outputs |
| `Edit` | Precise edits to existing files | Agents that modify code or documents |
| `Bash` | Execute shell commands | Agents that run scripts, git, CLI tools |
| `Glob` | Find files by pattern | Agents that search codebases |
| `Grep` | Search file contents | Agents that search for code patterns |
| `WebSearch` | Search the web | Agents that need external information |
| `WebFetch` | Fetch and parse web pages | Agents that read URLs |
| `AskUserQuestion` | Ask the user a structured question | Agents that need human input |

**Principle of least privilege**: Only include tools the agent actually needs. Fewer tools = clearer choices for the model = fewer mistakes.

---

## Subagents

Spawn specialized sub-agents for focused subtasks. Each subagent has its own context window and tool set.

### Spawning from an Orchestrator

In the Claude Agent SDK, subagents are spawned using the `Agent` tool:

```python
# In the orchestrator's tool set or via Claude's built-in Agent tool
# Claude will use it like this in its agentic loop:

# Agent tool call:
{
  "name": "Agent",
  "input": {
    "prompt": "Review this Python file for security vulnerabilities...",
    "description": "Security review of auth.py",
    "tools": ["Read", "Grep"],
    "allowed_tools": ["Read", "Grep"]
  }
}
```

### Subagent Design Tips

**Pass rich context in the spawn prompt.** The subagent has no memory of the parent conversation. Include:
- What to do (the task)
- What files/data to work with (paths, not contents — let it read them)
- What format to return results in
- Any constraints or special instructions

**Scope the tool set narrowly.** A security reviewer needs `Read` and `Grep`, not `Write` and `Bash`.

**Set max_turns for safety.** Prevents runaway subagents. 20-30 turns is usually plenty.

**Handle subagent failure in the orchestrator.** The orchestrator should check subagent results and retry or escalate if something went wrong.

---

## Sessions & Memory

### Sessions (Cross-Conversation Memory)

Sessions let an agent resume where it left off:

```python
# First conversation — capture session_id
session_id = None
async for message in query(prompt="Analyze this codebase"):
    if message.session_id and not session_id:
        session_id = message.session_id

# Later conversation — resume
async for message in query(
    prompt="Now refactor the auth module we discussed",
    session_id=session_id,
):
    ...
```

**When to use sessions:**
- Multi-step workflows where the user comes back later
- Agents that build up understanding over time (e.g., codebase familiarity)
- When context from a previous conversation is needed

**Session forking** — explore different approaches from the same starting point:
```python
async for message in query(
    prompt="Try approach B instead",
    session_id=session_id,  # forks from this point
):
    ...
```

### File-Based Memory

For persistent memory that outlives sessions:

```python
# Agent writes memory to a known location
# e.g., .agent-memory/project-context.json
# Future invocations read from this file
```

**When to use files over sessions:**
- Memory needs to be shared across different agents
- You want explicit control over what's remembered
- The memory format matters (structured data, not conversation history)

### Context Window Management

For long-running agents, plan for context compaction:
- The SDK automatically compresses older messages as the context fills up
- Critical information should be in the system prompt (always present) or re-readable from files
- Don't rely on the agent remembering details from early in a long conversation — have it write important findings to files and re-read them when needed

---

## Permissions & Safety

### Tool Permissions

```python
# Pre-approve safe tools (no user confirmation needed)
allowed_tools=["Read", "Glob", "Grep", "search_knowledge_base"]

# Block dangerous tools
disallowed_tools=["Bash", "Write"]

# The remaining tools require user approval per-use
```

### Permission Strategy by Agent Type

| Agent Role | Typically Allow | Typically Block | User Approval |
|-----------|----------------|-----------------|---------------|
| Read-only analyst | Read, Glob, Grep | Write, Edit, Bash | WebSearch |
| Code modifier | Read, Edit, Glob, Grep | Bash (risky commands) | Write (new files) |
| Autonomous worker | Read, Write, Edit, Bash, Glob, Grep | — | Destructive operations |
| Research agent | Read, WebSearch, WebFetch | Write, Bash | — |

### Safety Patterns

- **Confirmation before destructive actions**: Use `AskUserQuestion` before deletions, external API calls with side effects, or irreversible operations
- **Dry-run mode**: Have the agent describe what it *would* do before actually doing it
- **Audit logging via hooks**: Log all tool calls for review (see Hooks section)
- **Maximum iteration limits**: Set `max_turns` to prevent runaway agents

---

## Hooks

Run custom code at agent lifecycle events:

```python
from claude_agent_sdk import Hook, HookMatcher

hooks = [
    Hook(
        event="PreToolUse",
        matcher=HookMatcher(tool_name="Bash"),
        command="python validate_bash_command.py"
    ),
    Hook(
        event="PostToolUse",
        matcher=HookMatcher(tool_name=".*"),  # all tools
        command="python audit_log.py"
    ),
    Hook(
        event="Stop",
        command="python on_agent_complete.py"
    )
]
```

### Available Hook Events
- `PreToolUse` — Before a tool executes (can block/modify)
- `PostToolUse` — After a tool executes (for logging, validation)
- `Stop` — When the agent finishes its task
- `SessionStart` / `SessionEnd` — Session lifecycle

### When to Use Hooks
- **Audit logging**: Record all tool calls for compliance or debugging
- **Input validation**: Validate tool inputs before execution (e.g., block dangerous shell commands)
- **Notifications**: Alert when an agent completes a task or encounters an error
- **Metrics**: Track tool usage patterns, latency, token consumption

---

## Implementation Templates

### Single Agent Template

```
project/
├── agent.py (or agent.ts)     # Main entry point — query() call
├── tools/
│   ├── __init__.py
│   └── my_tools.py             # MCP server with custom tools
├── prompts/
│   └── system_prompt.md        # System prompt (loaded at runtime)
├── config.py                   # Environment, model, parameters
└── tests/
    └── test_agent.py           # Test cases
```

### Multi-Agent Template

```
project/
├── orchestrator.py             # Main entry — spawns subagents
├── agents/
│   ├── worker_a.py             # Worker A config + system prompt
│   ├── worker_b.py             # Worker B config + system prompt
│   └── synthesizer.py          # Final synthesis agent
├── tools/
│   ├── shared_tools.py         # Tools available to all agents
│   ├── worker_a_tools.py       # Tools specific to Worker A
│   └── worker_b_tools.py       # Tools specific to Worker B
├── coordination/
│   ├── task_list.py            # Shared task state management
│   └── message_bus.py          # Inter-agent communication
├── prompts/
│   ├── orchestrator.md
│   ├── worker_a.md
│   ├── worker_b.md
│   └── synthesizer.md
├── config.py
└── tests/
    ├── test_orchestrator.py
    ├── test_worker_a.py
    └── test_worker_b.py
```

### Model Selection Guidance

| Use Case | Recommended Model | Why |
|----------|-------------------|-----|
| Complex reasoning, architecture | `claude-opus-4-6` | Strongest reasoning and planning |
| General-purpose agent work | `claude-sonnet-4-6` | Best balance of capability and cost |
| High-volume, simple tasks | `claude-haiku-4-5` | Fast, cheap, good for routing and classification |
| Evaluator in eval-optimizer loop | `claude-sonnet-4-6` | Good judgment at lower cost than opus |
| Router / classifier agent | `claude-haiku-4-5` | Fast classification, minimal cost |
