"""Shared app configuration."""

from django.apps import AppConfig


class SharedConfig(AppConfig):
    """Configuration for shared app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "src.shared"
    verbose_name = "Shared Infrastructure"
