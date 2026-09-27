# Interview Playbook

How to get specifics out of a user who knows what they want but hasn't articulated it yet.
Read at the start of every run; come back to the question banks when a phase feels thin.

## Contents
- [Pull techniques](#pull-techniques)
- [Example cards](#example-cards)
- [Drill-deeper decompositions](#drill-deeper-decompositions)
- [Question banks by phase](#question-banks-by-phase)
- [When the interview goes sideways](#when-the-interview-goes-sideways)

## Pull techniques

Most users can recognize the right answer far more easily than they can describe it. These
techniques turn "describe your product" into "pick what's true".

- **Walk the scenario.** "A new manager signs up on Monday morning. What's the first screen they
  see? What do they click first? What would make them close the tab?" Step-by-step scenarios
  surface workflows, empty states and onboarding that a feature list hides.
- **Ask what goes wrong.** For every happy path: "What if they submit it twice? What if the
  payment fails halfway? What if two people edit it at once? What if they don't have permission?"
  Failure states are where builders guess most.
- **Name the counter-example.** "What should this definitely *not* do?" and "What would make this
  feel wrong?" produce Out of Scope items and anti-requirements that users rarely volunteer.
- **Calibrate with references, then diverge.** "Is the editing experience closer to Google Docs
  (live, collaborative) or to Stripe's dashboard (form, save, done)?" References speed things up,
  but always follow with "where should yours differ?" — a spec that says "like Notion" is not a spec.
- **Make them count.** "How many projects does a typical customer have — 3, 30, 3,000?" Numbers
  shape pagination, search, performance and permissions far more than adjectives.
- **Force a cut.** "If this had to ship in two weeks, what would you drop first?" reveals true
  priority without restructuring the spec into MVP tiers.
- **Replay it back wrong on purpose (sparingly).** A recap with one deliberate simplification
  ("so anyone on the team can delete a project?") often draws out a rule the user assumed was
  obvious.
- **Hunt contradictions.** If "admins see everything" and "clients' data is private to them" are
  both true, ask which wins for an admin viewing client data.

## Example cards

Recap in plain text first when it helps, then call the tool.

**Scope (phase 1)**
```
AskUserQuestion({ questions: [{
  question: "What are we defining requirements for?",
  header: "Scope",
  multiSelect: false,
  options: [
    { label: "New product", description: "Nothing exists yet — we'll cover users, full workflows, and success criteria from scratch." },
    { label: "New feature", description: "Adding to an existing product — we'll focus on the new behavior and how it fits current users." },
    { label: "Change existing", description: "Modifying current behavior — we'll document what happens today, what should happen, and the migration impact." }
  ]
}]})
```

**Roles (multi-select, phase 2)**
```
AskUserQuestion({ questions: [{
  question: "Which kinds of users will interact with this?",
  header: "Roles",
  multiSelect: true,
  options: [
    { label: "End customer", description: "Uses the product to get their own job done; sees only their own data." },
    { label: "Team admin", description: "Manages members, settings and billing for their organization." },
    { label: "Internal staff", description: "Your support or ops people who help customers or moderate content." },
    { label: "API consumer", description: "Developers integrating with it rather than using the UI." }
  ]
}]})
```

**Drill deeper (after "standard login")**
```
AskUserQuestion({ questions: [{
  question: "Which sign-in methods should the first release support?",
  header: "Sign-in",
  multiSelect: true,
  options: [
    { label: "Email + password", description: "Classic credentials. Needs a password reset flow and lockout after repeated failures." },
    { label: "Magic link", description: "One-time sign-in link by email. No passwords to forget, but sign-in depends on email arriving quickly." },
    { label: "Google / GitHub", description: "Social sign-in. Which providers, and what happens to an account if the provider is unavailable?" },
    { label: "Company SSO", description: "Organization-managed identity (Okta, Azure AD). Who sets it up, and can SSO orgs also use passwords?" }
  ]
}]})
```

**Comparing concrete alternatives with `preview`**
```
AskUserQuestion({ questions: [{
  question: "Which approval flow matches how your team actually works?",
  header: "Approvals",
  multiSelect: false,
  options: [
    { label: "Single approver (Recommended)", description: "One manager approves; fastest, matches what you described for small teams.",
      preview: "Employee submits → Manager approves/rejects → Finance sees approved only\nRejected → back to employee with a required comment" },
    { label: "Two-step", description: "Manager, then finance. Slower, but catches policy violations before payout.",
      preview: "Employee submits → Manager approves → Finance approves → Paid\nEither can reject → back to employee with a required comment" }
  ]
}]})
```

**Recap confirmation**
```
AskUserQuestion({ questions: [{
  question: "Does this capture the invoicing workflow correctly?",
  header: "Confirm",
  multiSelect: false,
  options: [
    { label: "Yes, continue", description: "Accurate — move on to the next area." },
    { label: "Mostly right", description: "A few details to fix — I'll say which in the notes." },
    { label: "Needs rework", description: "The core understanding is off — let's redo this area." }
  ]
}]})
```

**Depth check before writing**
```
AskUserQuestion({ questions: [{
  question: "Is this detailed enough to write the requirements docs?",
  header: "Depth",
  multiSelect: false,
  options: [
    { label: "Yes, write the docs", description: "Workflows, rules and acceptance criteria are specific enough for the architect and the build team." },
    { label: "Drill the gaps first", description: "Stay in interview mode for the open items I listed." },
    { label: "Speed path", description: "Fill the remaining gaps with my recommended answers, each labeled as an Assumption." }
  ]
}]})
```

## Drill-deeper decompositions

Vague phrases users reach for, and the concrete choices hiding inside them. Use these as starting
options, tailored to the product — don't paste them verbatim.

| Vague phrase | Decompose into |
|---|---|
| "standard login" | email+password / magic link / social providers / SSO; password reset; session length; "remember me"; lockout |
| "basic CRUD" | who can create / edit / delete each thing; soft vs hard delete; undo; audit trail; bulk actions; required fields and limits |
| "notifications" | which events; which channels (in-app, email, push, SMS); per-user preferences; digest vs instant; who receives each |
| "admin panel" | which admin actions exist; which roles get them; impersonation or not; audit of admin actions |
| "reports / analytics" | which questions they answer; filters and time ranges; export formats; freshness (live vs daily); who can see them |
| "real-time" | what must update without refresh; acceptable delay (instant, seconds, minutes); what happens on conflicting edits |
| "search" | what's searchable; exact vs fuzzy; filters and sorting; result limits; permissions on results |
| "payments" | one-off vs subscription; plans and trials; refunds; failed payment behavior; invoices/receipts; tax/currency |
| "multi-tenant / teams" | how orgs are created; invites; roles within an org; can a user belong to several orgs; data isolation |
| "import / export" | formats; size limits; validation and error reporting; partial success behavior; who can run it |
| "mobile friendly" | responsive web vs native; which workflows must work on a phone; offline expectations |
| "secure / compliant" | which regulations (GDPR, HIPAA, SOC 2); data retention and deletion; audit needs; who can see PII |
| "like {product}" | which specific behaviors to copy; where this product should differ; what to leave out |
| "fast" | which interactions; "instant" vs "a few seconds" vs "overnight"; expected data volume |

## Question banks by phase

Pick what applies; don't ask everything.

**Big picture** — What's the one-sentence pitch? Who feels the pain today, and how do they cope?
What happens if this never gets built? What would make you call it a success in three months —
signups, time saved, fewer support tickets, revenue? Is there a deadline or event driving it?

**Users and workflows** — What distinguishes each role? How often does each use it (hourly,
weekly, once)? How technical are they? Walk me through the most important thing each role does,
step by step. What does the very first session look like? What's the most common mistake users
will make, and what should happen then?

**Functional** — For each capability: who can do it, what are the inputs and limits, what
changes afterward, who gets told? Which items move through states (draft → submitted →
approved)? Which transitions are allowed, by whom? What calculations exist, and how is rounding
handled? What gets emailed or notified, when, and to whom?

**Data (business level)** — What are the main things the system keeps track of? What belongs to
what? Who owns each thing? What happens to child items when a parent is deleted? How long must
data be kept, and can users delete their own?

**Non-functional** — How many users at launch and in a year? How many at the same moment? Which
screens must feel instant? How bad is an hour of downtime? Any accessibility commitments? Which
browsers/devices? Any regulated data?

**UI/UX** — What should it feel like — calm and minimal, dense and powerful, playful? Which
screen matters most? What's front and center on it? Any product whose feel you want to borrow?
What must work on a phone?

**Constraints** — Budget or timeline limits? Existing systems this must work with or replace?
Technical preferences (recorded as constraints)? What is definitely out of scope?

## When the interview goes sideways

- **The user rambles.** Recap the two or three decisions buried in it and confirm them with a card.
- **The user is stuck.** Offer three concrete directions as options with vivid descriptions; people
  unstick by reacting, not by generating.
- **The user answers "whatever you think".** Give your recommendation with its reasoning as the
  first option, and confirm. Record it as decided (they chose it), not as an assumption.
- **The user wants to jump to building.** Offer the speed path; don't silently skip the depth bar.
- **You've asked the same area twice.** Move on and record an Open Question — circling wastes
  more time than a documented gap.
