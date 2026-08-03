# Database

PostgreSQL is the required development, test-verification, and production database. Base settings use `django.db.backends.postgresql`, and the supported Python 3.14 adapter is `psycopg[binary]==3.3.4`.

## Configuration

Set these values in `.env` at the project root:

```dotenv
DB_ENGINE=django.db.backends.postgresql
DB_NAME=task_management_db
DB_USER=taskflow
DB_PASSWORD=replace-me
DB_HOST=localhost
DB_PORT=5432
```

Use a separate database such as `task_management_test` for integration testing. Never commit credentials.

## Schema

- `users.CustomUser` extends Django authentication with role, profile, contact, and audit fields.
- `users.UserProfile` stores organizational and preference data.
- `projects.Project` stores ownership, status, dates, and descriptive data.
- `projects.ProjectMember` joins users to projects with a `ProjectRole`.
- `tasks.Task` belongs to a project and records assignment, status, priority, dates, and completion.
- `tasks.TaskComment` belongs to a task and author.
- `activity.ActivityLog` records actor, event type, description, details, and generic target identity.

## Migration and persistence verification

```powershell
python manage.py migrate --noinput
python manage.py showmigrations
python manage.py shell
```

This verification was completed locally against PostgreSQL 18.4. A user, project, task, and comment created in one Django process were retrieved in a separate process. `connection.vendor` returned `postgresql`, and the complete 173-test suite also ran against PostgreSQL.

## Backups

Use `pg_dump` for logical backups and test restoration regularly. Restrict database accounts to required privileges, require TLS for remote connections, and monitor connection saturation and slow queries.
