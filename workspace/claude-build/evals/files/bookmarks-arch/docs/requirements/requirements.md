# Bookmarks API — Requirements

## Overview
A small HTTP API for saving and tagging bookmarks, used by a browser extension. Single user per API key.

## User Stories and Acceptance Criteria
- **US-1** — As a user, I want to save a bookmark so I can find it later.
  - **AC-1.1** — Given a valid API key, when POST /bookmarks with a URL and optional title, then 201 with the bookmark (id, url, title, createdAt).
  - **AC-1.2** — Given an invalid URL, when POST /bookmarks, then 400 `{"error":"invalid_url"}`.
  - **AC-1.3** — Given a URL already saved, when POST /bookmarks, then 409 `{"error":"duplicate"}`.
- **US-2** — As a user, I want to list and delete bookmarks.
  - **AC-2.1** — GET /bookmarks returns the caller's bookmarks newest first, 50 per page, with a `next` cursor.
  - **AC-2.2** — DELETE /bookmarks/:id returns 204; another key's bookmark returns 404.
- **US-3** — As a user, I want to tag bookmarks and filter by tag.
  - **AC-3.1** — PUT /bookmarks/:id/tags with a list of tags replaces the tags (lowercased, max 10, each 1–32 chars).
  - **AC-3.2** — GET /bookmarks?tag=x returns only bookmarks with that tag.

## Business Rules
- **BR-1** — Every request requires a valid API key in `Authorization: Bearer`; otherwise 401.
- **BR-2** — A key only ever sees its own bookmarks.

## Out of Scope
- Accounts, sharing, full-text search, a UI.
