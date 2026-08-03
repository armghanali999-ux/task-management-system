#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import pathlib
import sys


def main():
    """Run administrative tasks."""
    # C: drive safety check
    project_root = pathlib.Path(__file__).resolve().parent
    if not str(project_root).startswith("C:"):
        raise RuntimeError(
            f"⚠️  Safety Error: Project is not on C: drive!\n"
            f"Current path: {project_root}\n"
            f"Required path: C:\\Users\\ghori\\Desktop\\Project\\task-management-system"
        )

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
