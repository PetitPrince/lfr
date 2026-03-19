---
name: django-migrate
description: Generate and apply Django database migrations after model changes.
allowed-tools: Bash, Read, Glob, Grep
---

After model changes, handle migrations safely:

1. Run `python manage.py makemigrations` to generate migration files
2. Review the generated migration: read the file and run `python manage.py sqlmigrate <app> <migration_number>` to see the SQL
3. If the SQL looks correct, run `python manage.py migrate`
4. Run `python manage.py showmigrations` to confirm the migration was applied

If the migration involves destructive changes (dropping columns/tables, renaming fields), warn the user before applying.
