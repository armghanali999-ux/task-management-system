"""
Shared domain infrastructure.
Abstract base classes for repositories, services, and domain events.
Follows Clean Architecture and SOLID principles.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass
class DomainEvent:
    """Base class for all domain events."""

    event_id: str = ""
    entity_id: Any = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    event_type: str = ""

    def __post_init__(self):
        if not self.event_type:
            self.event_type = self.__class__.__name__


class Repository(ABC, Generic[T]):
    """
    Abstract Repository pattern following Clean Architecture.
    Provides CRUD operations for domain entities.
    Depends on abstractions, not implementations (DIP).
    """

    @abstractmethod
    def add(self, entity: T) -> None:
        """Add an entity to the repository."""
        pass

    def create(self, data: dict[str, Any]) -> T:
        """Create an entity from a mapping (implemented by ORM repositories)."""
        raise NotImplementedError

    def delete(self, entity_id: Any) -> None:
        """Conventional CRUD alias for :meth:`remove`."""
        self.remove(entity_id)

    @abstractmethod
    def remove(self, entity_id: Any) -> None:
        """Remove an entity from the repository."""
        pass

    @abstractmethod
    def update(self, entity: T) -> None:
        """Update an entity in the repository."""
        pass

    @abstractmethod
    def get_by_id(self, entity_id: Any) -> T | None:
        """Retrieve an entity by ID."""
        pass

    @abstractmethod
    def get_all(self, **filters) -> list[T]:
        """Retrieve all entities with optional filters."""
        pass

    @abstractmethod
    def filter(self, **criteria) -> list[T]:
        """Filter entities by criteria."""
        pass

    @abstractmethod
    def count(self, **filters) -> int:
        """Count entities with optional filters."""
        pass


class DomainService(ABC):
    """
    Abstract Domain Service.
    Encapsulates business logic that doesn't belong to a single entity.
    Follows Single Responsibility Principle (SRP).
    """

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the service logic."""
        pass


class ApplicationService(ABC):
    """
    Abstract Application Service.
    Orchestrates domain logic and persists changes.
    Acts as a use-case handler following Clean Architecture.
    """

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the use case."""
        pass


class EventPublisher(ABC):
    """
    Abstract Event Publisher.
    Publishes domain events using Observer pattern.
    """

    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """Publish a domain event."""
        pass

    @abstractmethod
    def subscribe(self, event_type: str, handler: Any) -> None:
        """Subscribe to a domain event."""
        pass


class Specification(ABC, Generic[T]):
    """
    Abstract Specification pattern.
    Encapsulates business rules in reusable objects.
    Implements Strategy pattern for flexible filtering.
    """

    @abstractmethod
    def is_satisfied_by(self, entity: T) -> bool:
        """Check if entity satisfies the specification."""
        pass

    def get_criteria(self) -> dict[str, Any]:
        """Get database query criteria from specification."""
        return {}


class UnitOfWork(ABC):
    """
    Abstract Unit of Work pattern.
    Manages database transactions and coordinates repository changes.
    """

    @abstractmethod
    def begin(self) -> None:
        """Begin a transaction."""
        pass

    @abstractmethod
    def commit(self) -> None:
        """Commit the transaction."""
        pass

    @abstractmethod
    def rollback(self) -> None:
        """Rollback the transaction."""
        pass

    @abstractmethod
    def __enter__(self):
        """Context manager entry."""
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass
