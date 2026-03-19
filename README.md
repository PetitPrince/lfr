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

- Admin UI: http://127.0.0.1:8000/admin/
- Organizer Dashboard: http://127.0.0.1:8000/organize/
- Player UI: http://127.0.0.1:8000/accounts/login/

### Create an organizer account

```bash
uv run python manage.py shell -c "
from accounts.models import User
User.objects.create_user('organizer@test.com', 'testpass123', role='organizer')
"
```

## Player flow

1. Organizer creates a run, adds castings, and generates invite links
2. Player opens their invite link (`/accounts/claim/<code>/`)
3. Player signs up or logs in, then claims their character
4. Player lands on the run's message board (`/r/<slug>/`)
5. From there they can create posts, browse the discover section, and comment

## URL structure

| Prefix | Purpose |
|--------|---------|
| `/admin/` | Django admin |
| `/organize/` | Organizer dashboard |
| `/accounts/` | Player auth (signup, login, logout, invite claiming) |
| `/runs/` | Player run list |
| `/r/<slug>/` | Run-scoped player pages (message board, posts, discover) |
| `/casting/` | Autocomplete JSON endpoints |

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
