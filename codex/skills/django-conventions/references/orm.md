# Django ORM reference

## Detecting N+1

- Tests: `django_assert_num_queries(n)` (pytest-django) around the view/serializer call.
- Dev: django-debug-toolbar or `connection.queries` with `DEBUG=True`.
- DRF: nested serializers are the most common source. Prefetch in `get_queryset()`,
  not in the serializer.

## Prefetch with filtering

```python
from django.db.models import Prefetch

posts = Post.objects.select_related("author").prefetch_related(
    Prefetch("comments", queryset=Comment.objects.filter(is_public=True).select_related("author"),
             to_attr="public_comments"),
)
```

## Aggregation pitfalls

- Two `annotate(Count(...))` over different joins multiply rows. Use `Count(..., distinct=True)`
  or `Subquery`.
- `Subquery(... .values("x")[:1])` with `OuterRef` for "latest related row".
- `.distinct()` combined with `order_by` on a related field changes results. Check the SQL (`str(qs.query)`).

## Transactions

- `ATOMIC_REQUESTS` is off unless the project turned it on. Know which one you're in.
- `select_for_update(skip_locked=True)` implements a simple job queue.
- Catch `IntegrityError` **inside** a nested `atomic()`. Otherwise the outer transaction is broken.

## Large data

- `.iterator(chunk_size=2000)` avoids caching the whole result.
- Batch updates: iterate PK ranges and run `filter(pk__range=...).update(...)` with a short
  transaction per batch.
- `QuerySet.explain(analyze=True)` runs the query. Use it only on read queries.
