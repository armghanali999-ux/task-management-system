# TaskFlow Task Management System

TaskFlow is a Django and Django REST Framework application for managing users, projects, tasks, comments, activity, and dashboard reporting. The codebase demonstrates layered and Clean Architecture concepts through repositories, application services, dependency injection, strategies, and domain events.

## Verified status

- Python 3.14 is the primary runtime.
- The complete automated suite contains 173 tests and passes against PostgreSQL with 84.42% coverage.
- Black, Ruff, and mypy passed before the latest frontend/template additions; rerun the commands below before release.
- PostgreSQL is the required database. The Python 3.14 driver is `psycopg[binary]==3.3.4`.
- PostgreSQL 18.4 migrations and cross-connection persistence have been verified locally.
- GitHub publishing and Render deployment are intentionally paused at the customization checkpoint.

## Features

- Token authentication, registration, login, logout, user profiles, and roles
- Project CRUD, ownership, membership, status, dates, and progress
- Task CRUD, assignment, priority, status, deadlines, and completion
- Task comments and event-driven activity logging
- User and administrator dashboard metrics
- Responsive server-rendered pages enhanced by a small REST API client

## Setup (Windows, Python 3.14)

```powershell
py -3.14 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements\base.txt
python -m pip install -r requirements\dev.txt
Copy-Item .env.example .env
```

Create the PostgreSQL databases and set `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT` in `.env`. Do not use SQLite for final development or production verification.

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. Frontend pages are available at `/login/`, `/register/`, `/dashboard/`, `/projects/`, `/tasks/`, `/activity/`, and `/profile/`.

## Quality checks

```powershell
python -m pytest --cov=src --cov-report=term-missing --cov-report=html
python -m black --check .
python -m ruff check .
python -m mypy src
```

## Architecture map

- Domain abstractions and events: `src/shared/domain.py`
- Composition root and DI: `src/shared/composition.py`, `src/shared/di_container.py`
- Repositories: `src/users/repositories.py`, `src/projects/repositories.py`, `src/tasks/repositories.py`
- Application services: `src/users/services.py`, `src/projects/services.py`, `src/tasks/services.py`
- Factory: `src/shared/di_container.py`
- Strategy: `src/shared/strategies.py`, consumed by `src/shared/dashboard.py`
- Observer/domain-event bridge: `src/shared/events.py`, `src/activity/events.py`
- Presentation: app `views.py` files, `templates/`, and `static/`

See `docs/architecture.md`, `docs/design-patterns.md`, `docs/database.md`, `docs/customization.md`, `docs/deployment.md`, and `docs/api.md` for details.

## Deployment hold

Do not publish this repository or deploy it until customization is approved and the PostgreSQL persistence and browser workflow checks have passed.
