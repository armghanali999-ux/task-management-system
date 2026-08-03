"""Development-specific Django settings."""

from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Development-specific apps
INSTALLED_APPS += [  # noqa: F405
    "django_extensions",
]

# Development inherits the PostgreSQL configuration from base settings.

# Email
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Security (disabled in development)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}
