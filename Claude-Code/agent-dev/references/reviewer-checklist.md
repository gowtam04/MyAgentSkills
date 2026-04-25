# Agent Reviewer Checklist

The reviewer applies this checklist in addition to standard architecture and requirement-spec compliance. The reviewer also invokes the `claude-api` skill for SDK-level compliance checks.

Include the path to this file in the reviewer's spawn prompt. The reviewer reads it when starting the review and uses it to structure findings.

## Prompt structure
- Role, goal, behavior rules, tool-use guidance, output contract, few-shot examples — present in that order in the system prompt.
- Stable content first (system prompt, shared context, few-shot block), variable content last (user message, retrieved data). Prompt caching depends on this ordering.

## XML and formatting
- Long input sections wrapped in XML tags (`<ticket>`, `<policy>`, `<context>`) per `prompts.md`.
- No markdown where XML is specified; no inconsistent formatting across sections.

## Few-shot quality
- Each example conforms to the final output schema.
- At least one example covers an edge case (not just happy path).
- Examples are placed inside the cached block, not after the variable user input.

## Prompt-caching boundaries
- System prompt, shared context, and few-shot block are marked for caching per `agents.md`.
- Variable user data and retrieved chunks are outside the cached block.
- Use the `claude-api` skill to confirm correct `cache_control` placement in the SDK call.

## Tool description clarity
- Descriptions are written for the model — concrete, action-oriented, 1-3 sentences.
- Input schemas match `tools.md` field-for-field (names, types, descriptions, required flags, enums).
- Error returns are structured objects the model can reason about, not thrown exceptions.
- Destructive tools have confirmation patterns if `tools.md` calls for them.

## Structured-output tool
- If the spec uses tool-use as the structured output mechanism, the tool is present, named as specified, and is the final action the agent takes.
- Output schema matches `output-formats.md` exactly.

## SDK-level compliance (use `claude-api` skill)
- Prompt-caching config correct (cache breakpoints, TTL selection).
- Tool-use loop shape correct (accumulate tool results, max-iterations guard, safe termination).
- Extended thinking on/off per `agents.md`.
- Streaming on/off per `agents.md`.
- Retry policy and timeouts appropriate for the model and task.

## Guardrails
- Guardrails listed in `integration.md` (PII stripping, rate limits, output filters) are implemented in orchestration code, not in the prompt.
- Eval cases for leak attempts exist if the agent handles sensitive data.

## Output classification

- **MUST-FIX** — blocking issues (spec mismatch, schema mismatch, missing guardrail, broken control flow, SDK misuse).
- **SHOULD-FIX** — quality improvements (better tool descriptions, clearer prompt structure, additional few-shot examples).

The 3-cycle MUST-FIX ceiling applies only to code-level fixes. Prompt-quality findings about few-shot coverage or prompt structure that affect *observable* agent behavior belong to the Step 5 prompt-iteration cycle in the main skill, not the 3-cycle fix loop.
