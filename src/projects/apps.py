"""Projects app configuration."""

from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    """Configuration for projects app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "src.projects"
    verbose_name = "Projects Management"
