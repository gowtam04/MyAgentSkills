# AskQuestion Examples

Use structured cards for decisions that need an answer. Recap in plain text first when helpful, then call `AskQuestion`.

Cursor options are `{id, label}` only — **no description field**. Teach tradeoffs in the prose immediately before the card, and put the implication in the label. Parameter for multi-pick is **`allow_multiple`**. "Other" is always available.

## Example 1: Scope of work

Prose first: we need to know whether this is greenfield, a new feature, or a change — that decides how deep the interview goes.

```
AskQuestion:
  questions:
    - id: scope
      prompt: "What are we defining requirements for?"
      allow_multiple: false
      options:
        - id: greenfield
          label: "New product / greenfield — full personas, workflows, and success criteria"
        - id: feature
          label: "New feature in an existing product — focus on the delta and how it fits current users"
        - id: change
          label: "Change to existing behavior — current vs desired, edge cases, migration impact"
```

## Example 2: Roles (multi-select)

```
AskQuestion:
  questions:
    - id: roles
      prompt: "Which user roles matter for the first release?"
      allow_multiple: true
      options:
        - id: customer
          label: "End customer / consumer — people using the product to achieve a goal"
        - id: admin
          label: "Internal operator / admin — staff who configure, moderate, or support"
        - id: partner
          label: "Partner / external collaborator — limited shared access or data"
        - id: api
          label: "Developer / API consumer — integrators, not the primary UI"
```

## Example 3: Drill-deeper after a vague answer

User said "standard login" or picked a vague option. Do not advance — decompose:

```
AskQuestion:
  questions:
    - id: signin
      prompt: "What should sign-in support for the first release?"
      allow_multiple: true
      options:
        - id: password
          label: "Email + password — needs reset flow and basic lockout/rate limits"
        - id: magic
          label: "Magic link / passwordless email — simpler passwords; depends on email delivery"
        - id: social
          label: "Social login (Google/GitHub/etc.) — name providers; what if the provider is down?"
        - id: sso
          label: "SSO / enterprise IdP — who configures it, and who is excluded?"
```

## Example 4: Confirmation after a recap

After a short prose summary of what you heard:

```
AskQuestion:
  questions:
    - id: confirm
      prompt: "Does this capture the product correctly so far?"
      allow_multiple: false
      options:
        - id: yes
          label: "Yes — continue to the next interview area (or write docs if discovery is complete)"
        - id: mostly
          label: "Mostly right — I will correct a few details; keep the rest"
        - id: rework
          label: "Needs rework — core understanding is off; restart this section"
```

## Example 5: Depth-bar check before writing docs

After a plain-text summary of what is solid vs still open:

```
AskQuestion:
  questions:
    - id: depth
      prompt: "Is discovery deep enough to write the requirements docs?"
      allow_multiple: false
      options:
        - id: write
          label: "Yes — write the docs. Workflows, rules, and ACs are specific enough for architecture."
        - id: drill
          label: "Drill a few gaps first — stay in interview mode; I will name what is still fuzzy"
        - id: speed
          label: "Speed path — label remaining gaps as confirmed Assumptions, then write docs"
```

## Option quality

- Prefer realistic choices with tradeoffs in the **label** (Cursor has no option description field).
- Put a recommended default first when you have a justified recommendation.
- Do not pad with obviously bad options.
- 1–3 questions per call; batch only when tightly related.
- When the user is vague, prefer a drill-deeper card over accepting the vagueness.
