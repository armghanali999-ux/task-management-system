"""
Event publishing system for domain events.
Implements Observer pattern with in-memory event bus.
"""

import logging
from collections.abc import Callable

from src.shared.domain import DomainEvent, EventPublisher

logger = logging.getLogger(__name__)


class InMemoryEventBus(EventPublisher):
    """In-memory event bus for domain events."""

    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = {}
        self._event_history: list[DomainEvent] = []

    def publish(self, event: DomainEvent) -> None:
        """Publish an event to all subscribers."""
        self._event_history.append(event)
        event_type = event.event_type

        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}", exc_info=True)

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def get_event_history(self, event_type: str | None = None) -> list[DomainEvent]:
        """Get event history, optionally filtered by type."""
        if event_type:
            return [e for e in self._event_history if e.event_type == event_type]
        return self._event_history.copy()

    def clear_history(self) -> None:
        """Clear event history."""
        self._event_history.clear()


# Global event bus instance
event_bus = InMemoryEventBus()
