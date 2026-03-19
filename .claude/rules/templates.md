---
paths:
  - "**/templates/**/*.html"
---

When writing Django templates:
- HTMX partials go in a `partials/` subdirectory and should not extend base templates
- Full page templates extend the base layout
- Always include `{% csrf_token %}` in forms
- Use `hx-target` and `hx-swap` explicitly rather than relying on defaults
- Escape user content — use `{{ variable }}` (auto-escaped), never `{{ variable|safe }}` unless the content has been sanitized
