# Customization checkpoint

Deployment is paused until the product owner approves the following choices.

| Item | Current value |
|---|---|
| Application name | TaskFlow / Task Management System |
| Theme | Bootstrap 5.1 with light and dark theme support |
| Colors | Bootstrap primary blue; success green; info cyan; danger red |
| Logo | Text/clipboard treatment; no final image asset |
| User roles | Admin, Project Manager, Team Member |
| Project statuses | Planned, Active, On Hold, Completed, Cancelled |
| Task statuses | To Do, In Progress, Under Review, Completed, Cancelled |
| Task priorities | Low, Medium, High, Critical |
| Dashboard cards | Projects, Tasks, In Progress, Overdue |
| Navigation | Home/brand, Dashboard, Projects, Tasks, Activity, Profile, Logout; Login/Register when signed out |

After approval, update model choice labels only with a migration-safe plan. Cosmetic changes belong in `templates/base.html`, `static/css/theme.css`, and static image assets. Navigation and dashboard changes belong in the corresponding templates and `static/js/frontend.js`.
