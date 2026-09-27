# Team Expenses — Requirements

## Overview
A web app for a 40-person agency to submit, approve, and reimburse expenses. Today it's email and a
spreadsheet; receipts get lost and reimbursements take 3+ weeks. Success: median submit-to-paid
under 7 days, zero lost receipts.

## Users and Roles
| Role | Goals | Can | Cannot |
|---|---|---|---|
| Employee | Get reimbursed fast | Submit and view own expenses | See others' expenses |
| Manager | Approve their team's spend | Approve/reject direct reports' expenses | Approve their own |
| Finance | Pay approved expenses | See all, mark paid, export | Approve |

## User Stories and Acceptance Criteria
- **US-1** — As an employee, I want to submit an expense with a receipt so that I get reimbursed.
  - **AC-1.1** — Given a signed-in employee, when they submit amount, date, category, description and a receipt (JPEG/PNG/PDF, max 10 MB), then the expense is saved with status Submitted.
  - **AC-1.2** — Given a missing receipt on an expense over $25.00, when they submit, then it is rejected with "Receipt required over $25".
- **US-2** — As a manager, I want to approve or reject my reports' expenses so that spend is controlled.
  - **AC-2.1** — Given a Submitted expense from a direct report, when the manager approves, then status becomes Approved and the employee is emailed.
  - **AC-2.2** — Given a rejection, when the manager rejects without a comment, then it is refused with "Comment required".
- **US-3** — As finance, I want to mark approved expenses paid and export them so that payroll can reimburse.
  - **AC-3.1** — Given Approved expenses, when finance marks a batch paid, then each becomes Paid with the paid date.
  - **AC-3.2** — Given a date range, when finance exports, then a CSV with employee, date, category, amount, status downloads.
- **US-4** — As an employee, I want to see the status of my expenses so that I know when I'll be paid.
  - **AC-4.1** — Given an employee with expenses, when they open My Expenses, then they see each expense's status, newest first.

## Business Rules
- **BR-1** — Status flow: Submitted → Approved | Rejected; Approved → Paid. No other transitions.
- **BR-2** — A manager can never approve an expense they submitted.
- **BR-3** — Amounts are in USD with two decimals; the $25.00 receipt threshold is inclusive of $25.01 and above.
- **BR-4** — Paid expenses are read-only to every role.

## Non-Functional
- 40 users, ~300 expenses/month. Pages load in under 2 s. Sign-in with Google Workspace accounts only.

## Constraints
- Budget: small; the owner prefers TypeScript. No mobile app.

## Out of Scope
- Mileage and per-diem, multi-currency, corporate cards, payroll integration (CSV only), mobile apps.
