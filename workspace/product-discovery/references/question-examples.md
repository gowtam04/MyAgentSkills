# ask_user_question Examples

Use structured cards for decisions that need an answer. Recap in plain text first when helpful, then call the tool.

Parameter name is **`multi_select`** (not `multiSelect`).

## Example 1: Scope of work

```
ask_user_question with one question:
  question: "What are we defining requirements for?"
  options:
    - label: "New product / greenfield app"
      description: "No existing product surface; we need personas, full workflows, and success criteria."
    - label: "New feature in an existing product"
      description: "We will focus on the delta from current behavior and how it fits existing users."
    - label: "Change to existing behavior"
      description: "We will document current vs desired behavior, edge cases, and migration impact."
  multi_select: false
```

## Example 2: Roles (multi-select)

```
ask_user_question:
  question: "Which user roles matter for the first release?"
  options:
    - label: "End customer / consumer"
      description: "People who use the product to achieve a personal or business goal."
    - label: "Internal operator / admin"
      description: "Staff who configure, moderate, or support the product."
    - label: "Partner / external collaborator"
      description: "People outside the org who share limited access or data."
    - label: "Developer / API consumer"
      description: "Integrators who consume APIs rather than the primary UI."
  multi_select: true
```

## Example 3: Confirmation after a recap

After a short prose summary of what you heard:

```
ask_user_question:
  question: "Does this capture the product correctly so far?"
  options:
    - label: "Yes — continue"
      description: "Move to the next interview area (or write docs if discovery is complete)."
    - label: "Mostly right — small fixes"
      description: "I will correct a few details; keep the rest."
    - label: "Needs rework"
      description: "Core understanding is off; restart this section."
  multi_select: false
```

## Option quality

- Prefer realistic choices with tradeoffs in the description.
- Put a recommended default first when you have a justified recommendation.
- Do not pad with obviously bad options.
- 1–3 questions per call; batch only when tightly related.
