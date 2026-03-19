---
name: generate-tests
description: Create pytest tests for Django models, views, or other modules. Use when writing new code or when asked to add tests.
allowed-tools: Read, Write, Glob, Grep, Bash
---

Generate tests for: $ARGUMENTS

Guidelines:
- Use pytest with pytest-django
- Use factories (factory_boy) over raw model creation where factories exist
- Test both happy paths and edge cases
- For views: test response status, template used, context data, and permissions
- For HTMX views: test that partial templates are returned and HX-* response headers are correct
- For models: test constraints, custom methods, and string representations
- Name tests descriptively: `test_<what>_<condition>_<expected>`
- Keep fixtures close to the tests that use them
