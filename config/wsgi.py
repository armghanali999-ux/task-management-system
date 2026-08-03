"""
WSGI config for task_management_system project.
It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
from pathlib import Path

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

# C: drive safety check
project_root = Path(__file__).resolve().parent.parent
if not str(project_root).startswith("C:"):
    raise RuntimeError(
        f"⚠️  Safety Error: Project is not on C: drive!\n"
        f"Current path: {project_root}\n"
        f"Required path: C:\\Users\\ghori\\Desktop\\Project\\task-management-system"
    )

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

application = get_wsgi_application()
application = WhiteNoise(application, root=project_root / "staticfiles")
