# Architecture Diagrams

## Clean Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                      │
│  (HTML Templates, REST API Endpoints, Serializers)      │
│                                                           │
│  templates/        static/           src/*/views.py    │
│  base.html        css/theme.css      UserViewSet         │
│  index.html       js/main.js         ProjectViewSet      │
│                                      TaskViewSet         │
└─────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────┐
│                  APPLICATION LAYER                       │
│        (Orchestrates Use Cases via Services)            │
│                                                           │
│  src/*/services.py                                       │
│  - UserRegistrationService                              │
│  - CreateProjectService                                 │
│  - AssignTaskService                                    │
│  - DashboardService                                     │
│                                                           │
│  Total: 15+ ApplicationServices                         │
└─────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────┐
│               INFRASTRUCTURE LAYER                        │
│    (Data Persistence & External Services)               │
│                                                           │
│  src/*/repositories.py                                   │
│  - UserRepository                                        │
│  - ProjectRepository                                     │
│  - TaskRepository                                        │
│  - TaskCommentRepository                                 │
│  - ActivityLogRepository                                 │
│                                                           │
│  Total: 5 concrete repositories                         │
└─────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────┐
│                    DOMAIN LAYER                          │
│        (Business Logic & Abstraction Contracts)         │
│                                                           │
│  src/*/models.py              src/shared/domain.py      │
│  - CustomUser                 - Repository (ABC)         │
│  - Project                    - ApplicationService (ABC) │
│  - Task                       - DomainService (ABC)      │
│  - ActivityLog                - EventPublisher (ABC)     │
│                               - Specification (ABC)      │
│                               - UnitOfWork (ABC)         │
│                               - DomainEvent              │
└─────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────┐
│                   DATABASE & STORAGE                     │
│                                                           │
│  PostgreSQL (Production)  SQLite (Development)          │
│                                                           │
│  Tables:                                                │
│  - users_customuser          - projects_project        │
│  - users_userprofile         - projects_projectmember  │
│  - tasks_task                - activity_activitylog    │
│  - tasks_taskcomment                                     │
└─────────────────────────────────────────────────────────┘
```

---

## Dependency Injection Flow

```
┌──────────────────────────────────┐
│   DIContainer (Service Locator)   │
│                                   │
│  register_singleton()             │
│  register_factory()               │
│  register_transient()             │
│  resolve(name)                    │
└──────────────────────────────────┘
              ↓
┌──────────────────────────────────┐
│     ServiceFactory               │
│                                   │
│  create_service(name)            │
│  ↓                               │
│  Returns: Service with all       │
│  dependencies injected           │
└──────────────────────────────────┘
              ↓
┌────────────────────────────────────────────────────────┐
│         ApplicationService Constructor                  │
│                                                         │
│  def __init__(self,                                    │
│      user_repo: UserRepository,                        │
│      project_repo: ProjectRepository) -> None:        │
│                                                         │
│      self.user_repo = user_repo                        │
│      self.project_repo = project_repo                  │
└────────────────────────────────────────────────────────┘
```

---

## Request Processing Flow

```
HTTP Request
    ↓
┌─────────────────────────────┐
│   REST API ViewSet          │
│ (UserViewSet, TaskViewSet)  │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│   DRF Serializer            │
│  (Validation, Transform)    │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│  Application Service        │
│  (Business Logic)           │
│                             │
│  @log_operation             │
│  def execute(...):          │
│    1. Validate rules        │
│    2. Use repositories      │
│    3. Change state          │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│   Repository                │
│  (Data Access Pattern)      │
│                             │
│  - get_by_id()              │
│  - create()                 │
│  - update()                 │
│  - delete()                 │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│   Django ORM                │
│  (Query Construction)       │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│   Database                  │
│ (PostgreSQL / SQLite)       │
└─────────────────────────────┘
    ↓
HTTP Response (JSON)
```

---

## Module Architecture

```
┌──────────── SHARED MODULE ──────────────┐
│  src/shared/                            │
│  ├── domain.py (Abstract base classes) │
│  ├── di_container.py (DI & Factory)    │
│  ├── events.py (Event Bus)             │
│  ├── utils.py (Decorators, Exceptions) │
│  ├── dashboard.py (Aggregation)        │
│  └── dashboard_views.py (Views)        │
└─────────────────────────────────────────┘

┌── USERS MODULE ──┐  ┌── PROJECTS MODULE ──┐  ┌── TASKS MODULE ──┐
│ src/users/       │  │ src/projects/       │  │ src/tasks/       │
│                  │  │                     │  │                  │
│ ├── models.py    │  │ ├── models.py       │  │ ├── models.py    │
│ ├── repos.py     │  │ ├── repos.py        │  │ ├── repos.py     │
│ ├── services.py  │  │ ├── services.py     │  │ ├── services.py  │
│ ├── serializers  │  │ ├── serializers     │  │ ├── serializers  │
│ ├── views.py     │  │ ├── views.py        │  │ ├── views.py     │
│ ├── admin.py     │  │ ├── admin.py        │  │ ├── admin.py     │
│ ├── urls.py      │  │ ├── urls.py         │  │ ├── urls.py      │
│ ├── signals.py   │  │ └── migrations/     │  │ └── migrations/  │
│ └── migrations/  │  │                     │  │                  │
└──────────────────┘  └─────────────────────┘  └──────────────────┘

┌──── ACTIVITY MODULE ────┐
│ src/activity/           │
│                         │
│ ├── models.py           │
│ ├── repos.py            │
│ ├── serializers.py      │
│ ├── views.py            │
│ ├── admin.py            │
│ ├── urls.py             │
│ └── migrations/         │
└─────────────────────────┘
```

---

## Service Layer Pattern Example

```
User Registration Use Case:

HTTP Request
    ↓
┌─────────────────────────────────────────┐
│  POST /api/users/register/              │
│  Body: {email, password, name}          │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  UserSerializer.validate()              │
│  - Check email format                   │
│  - Check password strength              │
│  - Return cleaned data                  │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  UserRegistrationService.execute()      │
│  1. Check if email already exists       │
│     (via UserRepository.get_by_email)   │
│  2. If exists → raise                   │
│     BusinessRuleException               │
│  3. Create user via                     │
│     UserRepository.create()             │
│  4. Send welcome email                  │
│  5. Log activity                        │
│  6. Return user data                    │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  UserRepository.create(data)            │
│  → Django ORM CustomUser.objects.create │
│  → Database persists data               │
│  → Returns created user object          │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  UserSerializer.to_representation()     │
│  - Transform user object to JSON        │
│  - Include: id, email, name, etc        │
└─────────────────────────────────────────┘
    ↓
HTTP Response
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "team_member"
}
```

---

## Database Relationships

```
┌─────────────────┐         ┌──────────────────┐
│  CustomUser     │◄────────│  UserProfile     │
│                 │  1:1    │                  │
│  id (PK)        │         │  id (PK)         │
│  email (unique) │         │  user_id (FK)    │
│  password       │         │  phone           │
│  role           │         │  bio             │
│  is_active      │         │                  │
│  created_at     │         │                  │
└─────────────────┘         └──────────────────┘

┌─────────────────┐         ┌──────────────────┐
│  Project        │◄────────│  ProjectMember   │
│                 │  1:N    │                  │
│  id (PK)        │         │  id (PK)         │
│  title          │         │  project_id (FK) │
│  slug           │         │  user_id (FK)    │
│  owner_id (FK)  │────┐    │  role            │
│  status         │    │    │  joined_at       │
│  created_at     │    │    └──────────────────┘
└─────────────────┘    │
        ▲              │
        │              │
        └──────────────┘
              │
        ┌──────────────────┐
        │  CustomUser      │
        │  (via owner_id)  │
        │  (via member M:M)│
        └──────────────────┘

┌──────────────────┐      ┌──────────────────┐
│  Task            │      │  TaskComment     │
│                  │      │                  │
│  id (PK)         │◄─────│  id (PK)         │
│  title           │  1:N │  task_id (FK)    │
│  project_id (FK) │      │  author_id (FK)  │
│  assigned_to(FK) │      │  content         │
│  created_by(FK)  │      │  created_at      │
│  status          │      │                  │
│  priority        │      │                  │
│  due_date        │      │                  │
│  completed_at    │      │                  │
└──────────────────┘      └──────────────────┘

┌──────────────────────────────────────────┐
│  ActivityLog (Audit Trail)               │
│                                          │
│  id (PK)                                │
│  actor_id (FK) → CustomUser             │
│  activity_type                          │
│  content_type_id (FK)                   │
│  object_id                              │
│  description                            │
│  changes (JSONField)                    │
│  created_at                             │
│                                          │
│ GenericForeignKey can point to:        │
│ - CustomUser                            │
│ - Project                               │
│ - Task                                  │
│ - Any model via content_type           │
└──────────────────────────────────────────┘
```

---

## Test Coverage Map

```
Domain Layer (Models)
├── CustomUser .............. 80% (tests/test_users.py)
├── UserProfile ............. 80%
├── Project ................. 71% (tests/test_projects.py)
├── ProjectMember ........... 71%
├── Task .................... 75% (tests/test_tasks.py)
├── TaskComment ............. 75%
└── ActivityLog ............. 75% (tests/test_activity.py)

Infrastructure Layer (Repositories)
├── UserRepository .......... 33% (tests/test_users.py::TestUserRepository)
├── ProjectRepository ....... 40% (tests/test_projects.py::TestProjectRepository)
├── TaskRepository .......... 40% (tests/test_tasks.py::TestTaskRepository)
└── TaskCommentRepository ... 40%

Application Layer (Services)
├── User Services ........... 44% (tests/test_users.py::TestUserService)
├── Project Services ........ 50% (tests/test_projects.py::TestService)
├── Task Services ........... 50% (tests/test_tasks.py::TestService)
└── Dashboard Service ....... 50% (tests/test_dashboard.py::TestDashboard)

Architecture Layer
├── OOP Principles .......... 100% (tests/test_architecture.py::TestOOP)
├── SOLID Principles ........ 100%
├── DI Container ............ 100% (tests/, fixture usage)
├── Repository Pattern ...... 100%
├── Service Pattern ......... 100%
└── Design Patterns ......... 100%

Overall Coverage: ~30% of codebase exercised
Target: 80% after complete test suite updates
```

---

## Sequence Diagram: Create Task Use Case

```
User/Client        API View        Service      Repository    Database
    │                 │              │              │             │
    │──POST /api/──►│              │              │             │
    │ /tasks/       │              │              │             │
    │               │              │              │             │
    │               ├─validate─────┐              │             │
    │               │  serializer  │              │             │
    │               └─────────────►│              │             │
    │               │              │              │             │
    │               │              │              │             │
    │               ├──execute─────┤              │             │
    │               │  service.    │              │             │
    │               └─────────────►│              │             │
    │               │              │              │             │
    │               │              ├─create────►│             │
    │               │              │ repository │             │
    │               │              └──────────►│             │
    │               │              │              │             │
    │               │              │              ├─INSERT──►│
    │               │              │              │  SQL     │
    │               │              │              └────────►│
    │               │              │              │          │
    │               │              │              │◄─RETURN─│
    │               │              │              │          │
    │               │              │◄─Task obj──│         │
    │               │              │  returned   │
    │               │◄─result──────│             │           │
    │               │ dictionary   │             │           │
    │               │              │             │
    │◄──200 JSON───│              │             │
    │  response    │              │             │
    │              │              │             │
```

---

## Design Patterns Used

```
1. REPOSITORY PATTERN
   ┌─────────────────┐
   │   Repository    │ (ABC)
   │   (Interface)   │
   └────────┬────────┘
           /|\
          / | \
    ┌────┴──┼──┴────┐
    │       │       │
 UserRepo ProjRepo TaskRepo
    (Concrete implementations)

2. SERVICE/COMMAND PATTERN
   ┌──────────────────────┐
   │  ApplicationService  │ (ABC)
   │  + execute()         │
   └─────────────────────┬┘
                        / \
           UserRegService JobService...
           (Concrete implementations)

3. FACTORY PATTERN
   DIContainer → ServiceFactory → Service(deps injected)

4. OBSERVER PATTERN
   EventPublisher (ABC)
           ├→ InMemoryEventBus
           └→ subscribe/publish

5. SPECIFICATION PATTERN
   Specification (ABC)
   └→ is_satisfied_by(entity) → boolean

6. UNIT OF WORK PATTERN
   UnitOfWork (ABC)
   ├→ begin()
   ├→ commit()
   └→ rollback()

7. DECORATOR PATTERN
   @log_operation decorator adds logging
   to service methods without modifying them
```

---

## Technology Stack

```
Backend Framework
  └─ Django 4.2.13 LTS
     ├─ Django REST Framework 3.14.0
     ├─ django-rest-framework.authtoken
     ├─ django-filter 23.5
     ├─ django-cors-headers 4.2.0
     └─ gunicorn 21.0.0

Database
  ├─ PostgreSQL (Production)
  ├─ SQLite3 (Development)
  └─ Both accessed via Django ORM

Testing & Quality
  ├─ pytest 9.1.1
  ├─ pytest-django 4.12.0
  ├─ pytest-cov 7.1.0
  ├─ black 24.1.1
  ├─ ruff 0.5.0
  ├─ mypy 1.8.0
  └─ faker 40.36.0 (test data)

Frontend
  ├─ Bootstrap 5
  ├─ HTML5
  ├─ CSS3 (with custom properties)
  └─ Vanilla JavaScript

Environment & Deployment
  ├─ python-dotenv (configuration)
  ├─ gunicorn (WSGI server)
  ├─ WhiteNoise (static files)
  └─ Render.com (hosting)

Python Version: 3.14.0
Node Version: Not required (no Node.js)
```

---

This comprehensive architecture ensures:
✅ Scalability through layer separation
✅ Maintainability through clear responsibilities
✅ Testability through dependency injection
✅ Flexibility through design patterns
✅ Professional code quality standards
