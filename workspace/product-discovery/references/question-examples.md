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

## Example 3: Drill-deeper after a vague answer

User said "standard login" or picked a vague option. Do not advance — decompose:

```
ask_user_question:
  question: "What should sign-in support for the first release?"
  options:
    - label: "Email + password"
      description: "Classic credentials; needs reset flow and basic lockout/rate limits in product terms."
    - label: "Magic link / passwordless email"
      description: "User receives a one-time link; simpler passwords, depends on email delivery expectations."
    - label: "Social login (Google/GitHub/etc.)"
      description: "Third-party identity; document which providers and what happens if the provider is down."
    - label: "SSO / enterprise IdP"
      description: "Org-managed identity; document who configures it and who is excluded."
  multi_select: true
```

## Example 4: Confirmation after a recap

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

## Example 5: Depth-bar check before writing docs

After a plain-text summary of what is solid vs still open:

```
ask_user_question:
  question: "Is discovery deep enough to write the requirements docs?"
  options:
    - label: "Yes — write the docs"
      description: "Workflows, rules, and acceptance criteria are specific enough for architecture."
    - label: "Drill a few gaps first"
      description: "Stay in interview mode; I will name what is still fuzzy."
    - label: "Speed path — label assumptions"
      description: "Go fast: document remaining gaps as confirmed Assumptions, then write docs."
  multi_select: false
```

## Option quality

- Prefer realistic choices with tradeoffs in the description.
- Put a recommended default first when you have a justified recommendation.
- Do not pad with obviously bad options.
- 1–3 questions per call; batch only when tightly related.
- When the user is vague, prefer a drill-deeper card over accepting the vagueness.
