"""Bridge domain events to the persistent activity log."""

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from django.apps import apps

from src.activity.models import ActivityLog
from src.shared.domain import DomainEvent
from src.shared.events import event_bus


@dataclass
class ActivityEvent(DomainEvent):
    actor_id: int | None = None
    entity_type: str = ""
    description: str = ""
    details: dict[str, Any] = field(default_factory=dict)


def persist_activity(event: ActivityEvent) -> None:
    """Observer that converts an activity domain event into an audit record."""
    model = apps.get_model(event.entity_type)
    target = model.objects.get(pk=event.entity_id)
    ActivityLog.log_activity(
        actor_id=event.actor_id,
        activity_type=event.details.pop("activity_type"),
        content_object=target,
        description=event.description,
        details=event.details,
    )


def publish_activity(actor_id, activity_type, entity, description, details=None) -> None:
    """Publish a framework-neutral activity event through the Observer bus."""
    event_bus.publish(
        ActivityEvent(
            event_id=str(uuid4()),
            entity_id=entity.pk,
            actor_id=actor_id,
            entity_type=entity._meta.label,
            description=description,
            details={"activity_type": activity_type, **(details or {})},
        )
    )
