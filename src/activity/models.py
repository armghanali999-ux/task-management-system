"""Activity/Audit log models."""

import json
from typing import cast

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from src.users.models import CustomUser


class ActivityType(models.TextChoices):
    """Activity type choices."""

    CREATED = "created", "Created"
    UPDATED = "updated", "Updated"
    DELETED = "deleted", "Deleted"
    STATUS_CHANGED = "status_changed", "Status Changed"
    ASSIGNED = "assigned", "Assigned"
    COMMENTED = "commented", "Commented"
    MEMBER_ADDED = "member_added", "Member Added"
    MEMBER_REMOVED = "member_removed", "Member Removed"
    PROJECT_CREATED = "project_created", "Project Created"
    TASK_CREATED = "task_created", "Task Created"
    TASK_UPDATED = "task_updated", "Task Updated"
    USER_CREATED = "user_created", "User Created"
    USER_UPDATED = "user_updated", "User Updated"


class ActivityLog(models.Model):
    """
    Model for tracking activities and changes in the system.
    Implements Observer pattern for domain event logging.
    """

    # User performing the action
    actor = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="activities",
    )

    # What was affected
    activity_type = models.CharField(max_length=50, choices=ActivityType.choices, db_index=True)

    # Generic content type for tracking any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    # Description
    description = models.CharField(max_length=255)
    details = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "activity_activitylog"
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["activity_type", "created_at"]),
            models.Index(fields=["actor", "created_at"]),
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.actor.email} - {self.get_activity_type_display()} - {self.description}"

    @classmethod
    def log_activity(
        cls,
        activity_type: str,
        content_object,
        description: str,
        actor: CustomUser | None = None,
        details: dict | None = None,
        actor_id: int | None = None,
    ) -> ActivityLog:
        """
        Create an activity log entry.
        Convenience method for logging activities.
        """
        if details is None:
            details = {}
        if actor is None and actor_id is None:
            raise ValueError("Either actor or actor_id is required")

        content_type = ContentType.objects.get_for_model(content_object)
        values = {
            "activity_type": activity_type,
            "content_type": content_type,
            "object_id": content_object.id,
            "description": description,
            "details": details,
        }
        if actor is not None:
            activity = cls.objects.create(actor=actor, **values)
        else:
            assert actor_id is not None
            activity = cls.objects.create(actor_id=actor_id, **values)
        return activity

    def get_details(self) -> dict:
        """Get details as dictionary."""
        if isinstance(self.details, str):
            try:
                return cast(dict, json.loads(self.details))
            except json.JSONDecodeError:
                return {}
        return cast(dict, self.details or {})
