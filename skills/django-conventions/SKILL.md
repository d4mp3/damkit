---
name: django-conventions
description: Use when writing, reviewing or debugging Django or Django REST Framework code - models, ORM queries, views, serializers, permissions, migrations, settings, Celery tasks, GeoDjango, pytest-django tests.
paths:
  - "**/models.py"
  - "**/models/*.py"
  - "**/views.py"
  - "**/views/*.py"
  - "**/serializers.py"
  - "**/permissions.py"
  - "**/migrations/*.py"
  - "**/settings.py"
  - "**/settings/*.py"
  - "**/manage.py"
  - "**/conftest.py"
---

# Django conventions

Project conventions in CLAUDE.md and existing code win over this file. Read how the
project already does things (settings layout, service layer or fat models, test style)
before adding a new pattern.

## ORM: the rules that prevent real bugs

- **Query count is a correctness property.** Any loop over a queryset that touches a
  relation needs `select_related` (FK/1:1) or `prefetch_related` (M2M/reverse FK).
  Lock it in with `django_assert_num_queries` in tests.
- **Race-free updates:** `F()` expressions and `QuerySet.update()` for counters;
  `select_for_update()` inside `transaction.atomic()` for read-modify-write.
- **Uniqueness belongs to the database.** `get_or_create`/`update_or_create` race without
  a `UniqueConstraint`. Model `validate_unique` does not protect concurrent requests.
- **Side effects after commit:** emails, Celery tasks, webhooks go in
  `transaction.on_commit(...)`. Otherwise the worker reads rows that don't exist yet or
  were rolled back.
- `bulk_create`/`bulk_update`/`update()` skip `save()` and signals. Check nothing relies on them.
- Big tables: `.iterator(chunk_size=...)`, `.values()`/`.only()`, and `exists()` rather than `count()` / truthiness.

Details and query patterns: `references/orm.md`.

## Migrations

Migrations run against production data. Treat each one as a deploy step:

- Separate schema migrations from data migrations. `RunPython` uses `apps.get_model()`
  and always has a reverse (or an explicit `RunPython.noop` with a comment why).
- Inspect the SQL: `python manage.py sqlmigrate <app> <number>`. Check lock level with
  the postgres-postgis skill (`references/migrations-locking.md`).
- Indexes on populated tables: `AddIndexConcurrently` in a migration with `atomic = False`.
- New NOT NULL column on a large table: add nullable → backfill in batches → add constraint.
- CI runs `python manage.py makemigrations --check --dry-run`.

## DRF security (where real IDORs come from)

- Scope data in `get_queryset()` (e.g. `filter(owner=request.user)`). `has_object_permission`
  is **not** called for list endpoints or for `queryset.update()`.
- Never use `fields = "__all__"` on write serializers (mass assignment of `owner`, `is_staff`, …).
  Declare `read_only_fields` for server-controlled fields.
- Set `DEFAULT_PERMISSION_CLASSES` explicitly. Don't rely on AllowAny defaults.
- File uploads: validate size and content type server-side, and store outside the web root with generated names.

Full checklist: `references/security.md`.

## Settings & runtime

- Config from environment (django-environ / pydantic-settings). No secrets in settings files.
- `python manage.py check --deploy` must be clean for production settings.
- Behind a proxy/ingress: `SECURE_PROXY_SSL_HEADER`, `CSRF_TRUSTED_ORIGINS`, `ALLOWED_HOSTS`.
- `CONN_MAX_AGE` + PgBouncer in transaction mode: disable server-side cursors
  (`DISABLE_SERVER_SIDE_CURSORS = True`).
- Don't run migrations from the container entrypoint when replicas > 1. Use a Job or an ArgoCD PreSync hook.

## Tests

pytest-django + factory_boy. Use `--reuse-db` locally. Test permissions with at least two
users (owner and non-owner). A test that only checks the happy path of an authz rule
proves nothing.

## GeoDjango

Spatial fields, lookups and SRID handling: see the postgres-postgis skill. GeoDjango
needs system GDAL/GEOS/PROJ libraries at runtime; the container-images skill covers how to ship them.
