# API Design

(Omit this file for pure internal or non-API work.)

Full contract for external or major internal APIs. Scale detail to risk: high detail on security-sensitive or non-standard endpoints; lighter on conventional CRUD.

## Conventions

- Base path / versioning:
- Auth scheme:
- Error envelope (example):
- Pagination / filtering / sorting:
- Idempotency / rate limits (if relevant):

## Endpoints

### `{METHOD} {path}`

| | |
|--|--|
| Purpose | |
| Auth | required role / public |
| Request | fields + types + validation |
| Response | success shape |
| Errors | codes + when they occur |
| Side effects | emails, jobs, webhooks |
| Notes | retries, pagination, etc. |

## Internal Interfaces (optional)

For non-HTTP seams that builders could get wrong: function signatures, events, message shapes, error types.

## External Providers

| Provider | Owned by | Failure handling | Secrets |
|----------|----------|------------------|---------|
| | | | |
