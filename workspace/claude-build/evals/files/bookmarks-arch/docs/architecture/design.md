# Bookmarks API — Technical Design

Mode: PM
Budget Tier: hobby

## Overview
Node 20 + TypeScript + Fastify + SQLite (better-sqlite3). Each module registers its own routes; one
wiring phase composes the app.

## Requirements Reference
`docs/requirements/requirements.md`

## Data Model
- `api_keys(id, key_hash, created_at)`
- `bookmarks(id, key_id → api_keys, url, title, created_at)`, unique `(key_id, url)`, index `(key_id, created_at desc)`
- `tags(bookmark_id → bookmarks on delete cascade, tag)`, primary key `(bookmark_id, tag)`

## File Structure
```
package.json, tsconfig.json, vitest.config.ts          [p1]
smoke/run.mjs, smoke/checks/health.mjs                 [p1]
src/contracts/types.ts      — Bookmark, Page<T>, ApiError types      [p2]
src/contracts/errors.ts     — error codes + toHttp()                  [p2]
src/db/schema.sql, src/db/db.ts — connection, migrations              [p3]
src/auth/auth.ts            — bearer key → keyId, 401 otherwise (BR-1) [p4c]
src/auth/auth.test.ts                                                 [p4c tests]
src/bookmarks/service.ts    — create/list/delete, dedupe, cursor      [p4a]
src/bookmarks/routes.ts     — registerBookmarkRoutes(app)             [p4a]
src/bookmarks/bookmarks.test.ts                                       [p4a tests]
src/tags/service.ts         — replaceTags, filter by tag              [p4b]
src/tags/routes.ts          — registerTagRoutes(app)                  [p4b]
src/tags/tags.test.ts                                                 [p4b tests]
src/app.ts                  — builds Fastify app, registers modules   [p5]
smoke/checks/bookmarks.mjs  — create + list + tag round trip          [p5]
```

## Interface Definitions
- `authenticate(header: string | undefined): Promise<{ keyId: number } | ApiError>` — `ApiError{status:401, error:"unauthorized"}`
- `createBookmark(keyId, { url, title? }): Promise<Bookmark | ApiError>` — 400 invalid_url, 409 duplicate
- `listBookmarks(keyId, { cursor?, tag? }): Promise<Page<Bookmark>>` — 50 per page, newest first
- `deleteBookmark(keyId, id): Promise<void | ApiError>` — 404 when not the caller's
- `replaceTags(keyId, bookmarkId, tags: string[]): Promise<string[] | ApiError>` — lowercases; 400 `invalid_tags` if >10 or length outside 1–32
- `registerBookmarkRoutes(app)`, `registerTagRoutes(app)` — mount under `/bookmarks`, each route calls `authenticate` first

## Implementation Phases
- **p1 Scaffold** (scaffold) — project config, smoke runner. Depends on: none.
- **p2 Contracts** (contracts) — shared types and errors. Depends on: p1.
- **p3 Data** (data) — schema and db module. Depends on: p1.
- **p4a Bookmarks** (logic) — service + routes. Depends on: p2, p3. Refs: US-1, AC-1.1–1.3, US-2, AC-2.1, AC-2.2, BR-2.
- **p4b Tags** (logic) — service + routes. Depends on: p2, p3. Refs: US-3, AC-3.1, AC-3.2.
- **p4c Auth** (logic, high risk) — bearer auth. Depends on: p2, p3. Refs: BR-1.
- **p5 Wiring** (wiring) — app.ts and bookmark smoke check. Depends on: p4a, p4b, p4c.

## Parallel Waves
| Wave | Phases |
|---|---|
| 1 | p1 |
| 2 | p2, p3 |
| 3 | p4a, p4b, p4c |
| 4 | p5 |

**Critical path:** p1 → p2 → p4a → p5

## Build Manifest
```yaml
commands:
  install: "npm ci"
  test: "npx vitest run"
  test_one: "npx vitest run {files}"
  typecheck: "npx tsc --noEmit"
  build: "npx tsc -p ."
  smoke: "node smoke/run.mjs"
phases:
  - id: p1
    name: Scaffold
    kind: scaffold
    depends_on: []
    owns: ["package.json", "tsconfig.json", "vitest.config.ts", "smoke/run.mjs", "smoke/checks/health.mjs"]
    tests: []
    requirement_refs: []
    test_focus: "build and smoke pass on an empty app"
  - id: p2
    name: Contracts
    kind: contracts
    depends_on: [p1]
    owns: ["src/contracts/**"]
    requirement_refs: []
    test_focus: "typecheck"
  - id: p3
    name: Data
    kind: data
    depends_on: [p1]
    owns: ["src/db/**"]
    requirement_refs: []
    test_focus: "migrations apply to an empty database"
  - id: p4a
    name: Bookmarks
    kind: logic
    depends_on: [p2, p3]
    owns: ["src/bookmarks/service.ts", "src/bookmarks/routes.ts"]
    tests: ["src/bookmarks/bookmarks.test.ts"]
    requirement_refs: [US-1, AC-1.1, AC-1.2, AC-1.3, US-2, AC-2.1, AC-2.2, BR-2]
    test_focus: "create/dedupe/validate, pagination, ownership isolation"
  - id: p4b
    name: Tags
    kind: logic
    depends_on: [p2, p3]
    owns: ["src/tags/service.ts", "src/tags/routes.ts"]
    tests: ["src/tags/tags.test.ts"]
    requirement_refs: [US-3, AC-3.1, AC-3.2]
    test_focus: "tag normalization and limits, filter by tag"
  - id: p4c
    name: Auth
    kind: logic
    risk: high
    depends_on: [p2, p3]
    owns: ["src/auth/auth.ts"]
    tests: ["src/auth/auth.test.ts"]
    requirement_refs: [BR-1]
    test_focus: "missing/invalid/valid keys"
  - id: p5
    name: Wiring
    kind: wiring
    depends_on: [p4a, p4b, p4c]
    owns: ["src/app.ts", "smoke/checks/bookmarks.mjs"]
    requirement_refs: []
    test_focus: "smoke round trip"
integration_checkpoints:
  - name: api-e2e
    after: [p5]
    verifies: "create → list → tag → filter → delete over HTTP with two keys (US-1, US-2, US-3, BR-1, BR-2)"
```
