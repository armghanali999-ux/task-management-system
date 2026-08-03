"""Activity app configuration."""

from django.apps import AppConfig


class ActivityConfig(AppConfig):
    """Configuration for activity app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "src.activity"
    verbose_name = "Activity Tracking"

    def ready(self):
        """Register the persistent activity observer once Django is ready."""
        from src.activity.events import persist_activity
        from src.shared.events import event_bus

        event_bus.subscribe("ActivityEvent", persist_activity)
