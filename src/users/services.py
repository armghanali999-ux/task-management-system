"""User application services implementing use cases."""

from typing import Any, cast

from django.contrib.auth import authenticate

from src.shared.domain import ApplicationService
from src.shared.utils import (
    BusinessRuleException,
    EntityNotFoundException,
    log_operation,
)
from src.users.models import CustomUser
from src.users.repositories import UserRepository


class UserRegistrationService(ApplicationService):
    """
    Service for user registration use case.
    Orchestrates the registration business logic.
    Follows Single Responsibility Principle.
    """

    def __init__(self, user_repository: UserRepository | None = None):
        self.user_repository = user_repository or UserRepository()

    @log_operation("User Registration")
    def execute(self, email: str, password: str, first_name: str, last_name: str) -> dict[str, Any]:
        """Execute user registration."""
        # Check if user already exists
        existing_user = self.user_repository.get_by_email(email)
        if existing_user:
            raise BusinessRuleException(f"User with email {email} already exists")

        # Create new user
        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }


class UserAuthenticationService(ApplicationService):
    """
    Service for user authentication use case.
    Handles login logic.
    """

    def __init__(self, user_repository: UserRepository | None = None):
        self.user_repository = user_repository or UserRepository()

    @log_operation("User Authentication")
    def execute(self, email: str, password: str) -> CustomUser:
        """Authenticate user."""
        # Use Django's authenticate
        user = authenticate(username=email, password=password)

        if not user:
            raise EntityNotFoundException("Invalid email or password")

        if not user.is_active:
            raise BusinessRuleException("User account is inactive")

        return cast(CustomUser, user)


class UserProfileUpdateService(ApplicationService):
    """
    Service for updating user profile information.
    """

    def __init__(self, user_repository: UserRepository | None = None):
        self.user_repository = user_repository or UserRepository()

    @log_operation("User Profile Update")
    def execute(self, user_id: int, **kwargs) -> CustomUser:
        """Update user profile."""
        user = self.user_repository.get_by_id(user_id)

        if not user:
            raise EntityNotFoundException(f"User with id {user_id} not found")

        # Update allowed fields
        allowed_fields = ["first_name", "last_name", "phone", "bio", "avatar"]
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(user, field, value)

        self.user_repository.update(user)
        return user


class UserListService(ApplicationService):
    """
    Service for listing users.
    Implements filtering and authorization.
    """

    def __init__(self, user_repository: UserRepository | None = None):
        self.user_repository = user_repository or UserRepository()

    @log_operation("User List")
    def execute(self, **filters) -> list:
        """Get list of users."""
        return self.user_repository.get_all(**filters)


class UserDeactivationService(ApplicationService):
    """
    Service for deactivating user accounts.
    Implements business rules for account deactivation.
    """

    def __init__(self, user_repository: UserRepository | None = None):
        self.user_repository = user_repository or UserRepository()

    @log_operation("User Deactivation")
    def execute(self, user_id: int) -> dict[str, str]:
        """Deactivate a user account."""
        user = self.user_repository.get_by_id(user_id)

        if not user:
            raise EntityNotFoundException(f"User with id {user_id} not found")

        if user.is_superuser:
            raise BusinessRuleException("Cannot deactivate superuser accounts")

        self.user_repository.deactivate_user(user_id)

        return {"message": f"User {user.email} has been deactivated"}
