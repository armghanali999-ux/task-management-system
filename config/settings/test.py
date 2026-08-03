"""Test-specific Django settings."""

from .base import *  # noqa

DEBUG = True
TESTING = True

# PostgreSQL test database. Django creates and destroys this database per run.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("TEST_DB_NAME", default="task_management_test"),  # noqa: F405
        "USER": env("DB_USER", default="postgres"),  # noqa: F405
        "PASSWORD": env("DB_PASSWORD", default="postgres"),  # noqa: F405
        "HOST": env("DB_HOST", default="127.0.0.1"),  # noqa: F405
        "PORT": env("DB_PORT", default="5432"),  # noqa: F405
    }
}

# Disable password hashing for faster tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Use simple cache for testing
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Email
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
