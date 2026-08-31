# Data Model

Complete entity definitions grounded in requirements. Every entity and field should trace to a product need.

## Textual ERD

```text
User 1--* Order
Order *--* Product (via OrderLine)
```

## Entities

### {EntityName}

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | uuid / int | yes | |
| ... | | | |

- **Ownership:** who/what owns this record
- **Lifecycle:** create → active → archive/delete rules
- **Uniqueness / validation:** business constraints
- **Permissions:** who can read/write
- **Indexes / query patterns:** only when they shape architecture
- **Requirement trace:** story or FR id/path

## Relationships

| From | To | Cardinality | Cascade / constraints |
|------|-----|-------------|------------------------|
| | | | |

## Migrations And Seeds (if brownfield or multi-phase)

- Migration strategy (additive, dual-write, backfill)
- Seed/demo data needs
- Compatibility with existing data

**For build-team:** This file plus API/component interfaces is the primary contract for the test-author when writing tests before implementation.
