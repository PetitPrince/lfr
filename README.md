# LFR — Looking for Relation

Pre-game character relationship manager for Witchards LARP events.

## Setup

```bash
cd /Users/hoang/Project/lfr
uv sync --all-extras
```

## Run the dev server

```bash
source .venv/bin/activate
python manage.py migrate
python manage.py createsuperuser   # first time only
python manage.py runserver
```

Admin UI: http://127.0.0.1:8000/admin/
Organizer Dashboard: http://127.0.0.1:8000/organize/

### Create an organizer account

```bash
uv run python manage.py shell -c "
from accounts.models import User
User.objects.create_user('organizer@test.com', 'testpass123', role='organizer')
"
```

## Run tests

```bash
source .venv/bin/activate
pytest
```

## Reset the database

```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```
