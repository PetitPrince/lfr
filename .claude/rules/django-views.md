---
paths:
  - "**/views.py"
  - "**/views/**/*.py"
---

When writing Django views:
- Use `select_related()` for ForeignKey lookups and `prefetch_related()` for ManyToMany to avoid N+1 queries
- For HTMX requests, return partial templates (HTML fragments), not full pages. Check `request.headers.get('HX-Request')` to distinguish.
- Require authentication on protected views
- Check role permissions where applicable
