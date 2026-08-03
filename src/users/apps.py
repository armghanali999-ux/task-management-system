"""
Users app configuration.
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Configuration for users app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "src.users"
    verbose_name = "Users Management"

    def ready(self):
        """Import signals when app is ready."""
        import src.users.signals  # noqa
