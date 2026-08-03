"""Shared utility functions and exceptions."""

import logging
from functools import wraps
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class DomainException(Exception):  # noqa: N818 - established public domain name
    """Base exception for domain layer."""

    pass


class BusinessRuleException(DomainException):
    """Exception when a business rule is violated."""

    pass


class EntityNotFoundException(DomainException):
    """Exception when an entity is not found."""

    pass


class InvalidOperationException(DomainException):
    """Exception when an invalid operation is attempted."""

    pass


class PermissionDeniedException(DomainException):
    """Exception when user doesn't have permission."""

    pass


def memoize(func):
    """Memoization decorator for expensive operations."""

    cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return wrapper


def validate_not_empty(value: str | None, field_name: str = "value") -> str:
    """Validate that a string value is not empty."""
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty")
    return value.strip()


def validate_email(email: str) -> str:
    """Validate email format."""
    import re

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        raise ValueError(f"Invalid email format: {email}")
    return email


def log_operation(operation_name: str):
    """Decorator to log operation execution."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Operation started: {operation_name}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Operation completed: {operation_name}")
                return result
            except Exception as e:
                logger.error(f"Operation failed: {operation_name} - {e}")
                raise

        return wrapper

    return decorator
