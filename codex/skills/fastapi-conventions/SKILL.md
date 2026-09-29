---
name: fastapi-conventions
description: Use when writing, reviewing or debugging FastAPI services - routers, dependencies, Pydantic v2 models, async database access with SQLAlchemy 2.x, background work, lifespan, running under uvicorn/gunicorn in containers.
---

# FastAPI conventions

Existing project patterns win. Read how the app wires settings, DB sessions and routers first.

## The async trap (the most common production bug)

- `async def` endpoint + blocking call (sync DB driver, `requests`, GDAL/shapely on big data,
  `time.sleep`) blocks **the whole event loop**, so every request stalls.
- Rules: an endpoint that does blocking work is a plain `def` (FastAPI runs it in a
  threadpool). Or it offloads with `await anyio.to_thread.run_sync(fn)`. CPU-heavy work
  (validation of large geodata) goes to a worker/process pool or a job queue, not the request.
- Async all the way down: `asyncpg`/`psycopg` async + `AsyncSession`, and `httpx.AsyncClient`
  (shared, created in lifespan, not per request).

## Structure

- `lifespan` context manager for startup/shutdown (the `on_event` hooks are deprecated).
- Settings: `pydantic-settings` `BaseSettings`, injected via a cached dependency.
- DB session per request via a `yield` dependency. Commit/rollback there, not in handlers.
- Always declare `response_model` (or a return type annotation) so internal fields are never leaked.
- Separate schemas: `XCreate`, `XUpdate` (all optional), `XRead`. Never reuse ORM models as I/O.

## Errors

- Raise `HTTPException` for client errors. Register exception handlers for domain errors.
- Validation-style APIs (e.g. a geodata validator service): return a structured error list
  with 200/422 per your contract. Don't encode findings in HTTP status alone.

## Background work

`BackgroundTasks` runs in the same process after the response. It is lost on pod restart
and has no retries. Anything that must complete goes to a real queue (Celery, arq, RQ)
or is a Kubernetes Job.

## Running in containers

- One uvicorn process per container. Scale with replicas, not with `--workers`, in Kubernetes.
- `--proxy-headers --forwarded-allow-ips=...` behind an ingress.
- Graceful shutdown: set `--timeout-graceful-shutdown` below the pod's `terminationGracePeriodSeconds`.

## Tests

`httpx.AsyncClient(transport=ASGITransport(app=app))` + `pytest-asyncio`/`anyio`.
Override dependencies with `app.dependency_overrides`, and clear them after each test.
