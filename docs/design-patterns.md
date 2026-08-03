# Design patterns

## Repository

The abstract repository contract is in `src/shared/domain.py`. Concrete Django ORM repositories live in each feature package. Services call repository methods instead of embedding queries, and views obtain repositories through the composition root.

## Service

Each use case is represented by a focused service with an `execute()` method. Examples include `UserRegistrationService`, `CreateProjectService`, `AssignTaskService`, and `AddTaskCommentService` in the respective `services.py` modules.

## Dependency injection and factory

`src/shared/di_container.py` implements singleton, transient, and factory registrations plus `ServiceFactory`. `src/shared/composition.py` is the single application composition root. Views call `resolve()`; factories construct services with repository and event-bus dependencies.

## Strategy

`src/shared/strategies.py` defines the task metric strategy interface and concrete completion/overdue strategies. `src/shared/dashboard.py` selects and executes strategies to calculate dashboard percentages. Adding a new metric requires a new strategy, not changes to existing algorithms.

## Observer and domain events

`src/shared/events.py` provides `InMemoryEventBus`. Project and task services publish typed domain events. `src/activity/events.py` subscribes handlers that translate those events into durable `ActivityLog` rows. The observer bus decouples business operations from activity persistence.

## Specification

`Specification` in `src/shared/domain.py` encapsulates composable business predicates. It supports filtering rules without growing service conditionals.

## Production evolution

The in-memory event bus is appropriate for a single process. For multiple workers, preserve the publisher interface and replace the adapter with a transactional outbox and broker. This is an infrastructure change, not a use-case rewrite.
