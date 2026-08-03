# Deployment

Deployment is intentionally not authorized yet. Complete the customization checkpoint, PostgreSQL persistence test, quality gates, and browser/API smoke tests first.

## Required environment

- Python 3.14-compatible runtime
- PostgreSQL with TLS and managed backups
- Strong `SECRET_KEY`
- `DEBUG=False`
- Explicit `ALLOWED_HOSTS` and trusted CSRF origins
- Secure session/CSRF cookies and HTTPS redirect

## Release commands

```powershell
python -m pytest --cov=src --cov-fail-under=80
python -m black --check .
python -m ruff check .
python -m mypy src
python manage.py check --deploy --settings=config.settings.production
python manage.py migrate --noinput --settings=config.settings.production
python manage.py collectstatic --noinput --settings=config.settings.production
```

Start the WSGI process with Gunicorn on platforms that support it. Health checks should validate application response and database connectivity. Apply migrations as a release step before switching traffic.

## Rollback

Keep the prior application release available, use backward-compatible migrations, and take a verified database backup before destructive schema changes. Roll back application code first; reverse migrations only when explicitly tested as safe.

## Current hold

PostgreSQL migration, persistence, API workflows, and the automated suite have been verified locally. Visual browser automation is unavailable in the current session, although every frontend route returned HTTP 200 from the live server. No GitHub or Render action may occur until the user explicitly approves it.
