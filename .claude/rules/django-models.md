---
paths:
  - "**/models.py"
  - "**/models/**/*.py"
---

When writing Django models:
- Index fields that are frequently filtered on
- Use `on_delete=CASCADE` for children of owning objects, `PROTECT` for user references
- Use `select_related()` and `prefetch_related()` in related querysets and managers
