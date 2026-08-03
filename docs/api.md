# REST API

The API root prefix is `/api/`. Protected endpoints accept `Authorization: Token <token>` and also support authenticated Django sessions.

## Authentication and users

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/users/register/` | Register and return token/user |
| POST | `/api/users/login/` | Authenticate and return token/user |
| POST | `/api/users/logout/` | Delete current token |
| GET | `/api/users/me/` | Current profile |
| PATCH | `/api/users/update_profile/` | Update current profile |
| GET | `/api/users/` | List users subject to permissions |
| POST | `/api/auth/token/` | DRF token endpoint |

Registration accepts `email`, `first_name`, `last_name`, `password`, and `password_confirm`. Login accepts `email` and `password`.

## Projects

`/api/projects/` supports standard list/create/retrieve/update/delete operations. Create/update fields are `title`, `description`, `status`, `start_date`, and `end_date`. The authenticated creator becomes owner.

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/projects/{id}/members/` | List memberships |
| POST | `/api/projects/{id}/add_member/` | Add `user_id` with optional `role` |
| POST | `/api/projects/{id}/remove_member/` | Remove `user_id` |

## Tasks and comments

`/api/tasks/` supports standard CRUD. Creation accepts `project_id`, `title`, `description`, `priority`, `status`, `due_date`, `start_date`, and optional `assigned_to`.

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/tasks/{id}/assign/` | Assign `user_id` |
| POST | `/api/tasks/{id}/mark_completed/` | Complete task |
| GET | `/api/tasks/{id}/comments/` | List comments |
| POST | `/api/tasks/{id}/add_comment/` | Add comment with `content` |

## Activity and dashboards

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/activity/` | Read activity visible to current user |
| GET | `/api/dashboard/` | Current-user metrics |
| GET | `/api/admin-dashboard/` | Administrator system metrics |

List endpoints may return either a JSON list or DRF pagination object with `count`, `next`, `previous`, and `results`. Validation failures use HTTP 400, missing authentication 401/403, missing resources 404, successful creation 201, and successful deletion 204.
