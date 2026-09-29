# Safe schema changes (PostgreSQL 12+)

Always, in every migration: `SET lock_timeout = '5s';` and optionally `SET statement_timeout`.

| Change | Risk | Safe pattern |
|---|---|---|
| ADD COLUMN nullable, no default | metadata only | fine |
| ADD COLUMN with constant default | metadata only (PG11+) | fine |
| ADD COLUMN with volatile default (`now()`, `gen_random_uuid()`) | table rewrite | add nullable → backfill in batches → set default |
| SET NOT NULL | full scan under ACCESS EXCLUSIVE | `ADD CONSTRAINT c CHECK (col IS NOT NULL) NOT VALID` → `VALIDATE CONSTRAINT c` → `SET NOT NULL` (uses the check, PG12+) → drop the check |
| ALTER COLUMN TYPE | usually a rewrite | new column + dual write/backfill + swap. Exceptions: varchar(n) → larger or text |
| CREATE INDEX | blocks writes | `CREATE INDEX CONCURRENTLY` (not inside a transaction; Django: `AddIndexConcurrently`, `atomic = False`) |
| ADD FOREIGN KEY | locks both tables, scans | `ADD CONSTRAINT ... NOT VALID` → `VALIDATE CONSTRAINT` |
| ADD UNIQUE | index build | `CREATE UNIQUE INDEX CONCURRENTLY` → `ADD CONSTRAINT ... UNIQUE USING INDEX` |
| DROP COLUMN | fast, but app breaks | deploy code that no longer reads it first (Django: `SeparateDatabaseAndState`), then drop |
| RENAME COLUMN/TABLE | fast, but app breaks | expand/contract: add new → dual write → switch reads → drop old |

## Expand / contract

Every destructive change becomes two deploys: 1) expand (additive, old code still works),
2) contract (remove old, after all pods run new code). This is what makes rollback possible.

## Backfills

Batch by PK range, 1–10k rows per transaction, with a pause between batches. Never run a single
`UPDATE big_table SET ...` inside the migration transaction.

## Checking a migration

- Django: `python manage.py sqlmigrate app 0042`. Alembic: `alembic upgrade --sql`.
- Look for statements from the "table rewrite" / "full scan" rows above.
- Estimate the table size: `SELECT pg_size_pretty(pg_total_relation_size('tbl'));`
