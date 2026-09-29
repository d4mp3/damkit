---
name: postgres-postgis
description: Use when writing, reviewing or tuning PostgreSQL or PostGIS - SQL queries, indexes, EXPLAIN plans, schema migrations and locking, spatial queries (ST_Intersects, ST_DWithin, SRID, geometry vs geography), GeoDjango lookups, connection pooling, slow queries.
paths:
  - "**/*.sql"
  - "**/migrations/*.py"
  - "**/alembic/versions/*.py"
---

# PostgreSQL & PostGIS

## Evidence over intuition

Performance claims need a plan. Run (read queries only):

```sql
EXPLAIN (ANALYZE, BUFFERS, SETTINGS) <select ...>;
```

What to look for:
- **estimated vs actual rows** off by ≥10×: stale stats (`ANALYZE tbl`) or correlated predicates
- `Seq Scan` on a large table with a selective filter (`Rows Removed by Filter` large): missing or unusable index
- `Sort Method: external merge`: `work_mem` spill, or a missing index for the ORDER BY
- `Buffers: shared read` high: cold cache or reading too much. Compare with `hit`.
- Nested Loop with a large outer side: usually a misestimate

Never `EXPLAIN ANALYZE` INSERT/UPDATE/DELETE: it executes them. For workload-level
questions use `pg_stat_statements` (top by `total_exec_time`).

## Indexes

- B-tree composite: equality columns first, then range/sort column. `(tenant_id, created_at)`
  serves `WHERE tenant_id = ? ORDER BY created_at DESC`.
- Partial index for hot subsets: `WHERE deleted_at IS NULL`.
- Expression index must match the query expression exactly (`lower(email)`).
- `INCLUDE` columns enable index-only scans. BRIN for huge append-only time series.
- Every index costs writes and vacuum work. Don't add one without a query that needs it.

## Migrations & locks

Most outages from migrations come from lock queues, not from slow DDL: a statement that
needs `ACCESS EXCLUSIVE` waits behind a long transaction, and every query queues behind it.
Always set `SET lock_timeout = '5s'` in migrations and retry on failure.
Safe patterns per DDL: `references/migrations-locking.md`.

## PostGIS essentials

- **SRID discipline.** Store in a projected metric CRS when you compute distances or areas
  over a regional extent. For Poland that is EPSG:2180 (PUWG 1992). Use EPSG:4326 for
  interchange and web APIs, and EPSG:3857 only for tile rendering. Mixed SRIDs in one column
  are a bug: enforce with `geometry(MultiPolygon, 2180)`.
- `ST_DWithin(geom, :pt, 100)` on 4326 **geometry** means 100 *degrees*. Use metric geometry
  or `geography`.
- Index-killers: `ST_Distance(...) < x` (use `ST_DWithin`), `ST_Transform(column, ...)` in
  WHERE (transform the parameter instead, or add an expression index), and functions
  wrapping the indexed column.
- Validity: `ST_IsValid` / `ST_IsValidReason` before overlay operations. Fix invalid
  geometry with `ST_MakeValid`, then check that the geometry type didn't change (a polygon can become a GeometryCollection).
- Huge polygons (forest districts, admin boundaries): `ST_Subdivide` into a helper table
  so the index can prune.
- After bulk loads: `ANALYZE`. Spatial stats matter for the planner.

More (geography, joins, tiles, GeoDjango lookups): `references/postgis.md`.

## Connections

- Pod count × pool size × workers must stay below `max_connections` minus the reserve.
  Put PgBouncer (transaction mode) in front when you scale out.
- Transaction pooling breaks session state: `SET`, advisory locks, server-side cursors,
  and (in older setups) prepared statements.

## Diagnostics (read-only)

```sql
-- who blocks whom
SELECT pid, pg_blocking_pids(pid) AS blocked_by, state, wait_event_type, left(query, 80)
FROM pg_stat_activity WHERE cardinality(pg_blocking_pids(pid)) > 0;
-- long transactions
SELECT pid, now() - xact_start AS age, state, left(query, 80)
FROM pg_stat_activity WHERE xact_start IS NOT NULL ORDER BY age DESC LIMIT 10;
```
