# Django / DRF security checklist

Use as a lens, not a form to fill. Report only issues with a plausible attack path.

## Authorization
- `get_queryset()` scoped to the requesting user/tenant on every ViewSet
- Object-level permission on detail/update/delete; remember list endpoints skip it
- Custom actions (`@action`) have their own `permission_classes` if they differ
- Admin: `ModelAdmin.get_queryset` / `has_*_permission` for multi-tenant data

## Input & serialization
- No `fields = "__all__"` on writable serializers; `read_only_fields` for owner/status/flags
- `validate_<field>` for business constraints; DB constraints for invariants
- Raw SQL: `cursor.execute(sql, params)`. Never f-strings. Same for `.extra()` and `RawSQL`.
- `JSONField` lookups built from user keys: whitelist the keys

## Files
- Size limits (`DATA_UPLOAD_MAX_MEMORY_SIZE`, `FILE_UPLOAD_MAX_MEMORY_SIZE`, and the view level)
- Generated storage names, no user-controlled paths (path traversal)
- Serve user uploads from a separate domain/bucket or with `Content-Disposition: attachment`
- Geo uploads (zip shapefiles): zip-slip, zip bombs, GDAL virtual filesystem paths (`/vsicurl/`,
  `/vsizip/` built from user input can become SSRF)

## Session, CSRF, CORS
- `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY`, `SAMESITE`
- `CORS_ALLOW_ALL_ORIGINS=True` together with credentials is a vulnerability
- Token auth (JWT): short access-token lifetime, rotation, logout that actually invalidates

## Config
- `DEBUG=False`, `SECRET_KEY` from env, `ALLOWED_HOSTS` explicit
- `python manage.py check --deploy`
- Logging: no tokens, passwords or full request bodies in logs

## Abuse
- Rate limiting (DRF throttling) on login, password reset, signup, chat/message endpoints
- Pagination enforced (`PAGE_SIZE`, `max_page_size`) so nobody can dump a table in one request
