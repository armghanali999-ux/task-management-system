# Architecture

TaskFlow uses a pragmatic layered architecture. HTTP views and serializers form the presentation layer, application services coordinate use cases, repositories isolate persistence queries, and Django models represent the domain data and behavior. `src/shared/composition.py` is the composition root that binds these layers.

## Dependency direction

Requests enter through `src/*/views.py`. Views resolve application services or repositories by registered key. Services receive repository and event-publisher dependencies through constructors. Repositories own Django ORM access. This keeps workflow rules outside controllers and makes services independently testable.

## Exact implementation map

| Requirement | Implementation |
|---|---|
| OOP | `src/users/models.py`, `src/projects/models.py`, `src/tasks/models.py`; abstract base classes in `src/shared/domain.py` |
| SOLID | Small repository/service interfaces in `src/shared/domain.py`; constructor injection in app service modules; substitutable concrete repositories in app repository modules |
| Layered/Clean Architecture | presentation in `views.py` and serializers; application in `services.py`; persistence in `repositories.py`; shared abstractions in `src/shared/domain.py` |
| Dependency injection | registrations and resolution in `src/shared/composition.py`; container mechanics in `src/shared/di_container.py` |
| Repository pattern | `src/users/repositories.py`, `src/projects/repositories.py`, `src/tasks/repositories.py` |
| Service pattern | `src/users/services.py`, `src/projects/services.py`, `src/tasks/services.py`, `src/shared/dashboard.py` |
| Factory | `ServiceFactory` in `src/shared/di_container.py` |
| Strategy | task metric strategies in `src/shared/strategies.py`, selected by dashboard services in `src/shared/dashboard.py` |
| Observer/domain events | bus in `src/shared/events.py`; activity subscriber bridge in `src/activity/events.py`; publishers in project/task services |

## Composition lifecycle

The module-level container is built once when `src.shared.composition` loads. Repositories and the event bus are singletons; services are factories/transients so each resolution receives declared dependencies. Views use `resolve()` and do not assemble concrete services locally.

## Boundaries and tradeoffs

Django models necessarily depend on the ORM. Repositories contain complex query construction, while basic ViewSet querysets still provide DRF metadata. Domain events are in-process and synchronous; production workloads that require guaranteed delivery should add an outbox and background broker without changing service contracts.
