"""User domain repository patterns."""

from src.shared.domain import Repository
from src.users.models import CustomUser


class UserRepository(Repository):
    """
    Concrete implementation of User repository.
    Encapsulates user data access logic following Repository pattern.
    Depends on abstraction (Repository ABC).
    """

    def add(self, user: CustomUser) -> None:
        """Add a new user to the repository."""
        user.save()

    def create(self, data):
        """Create a user while preserving Django password hashing."""
        return CustomUser.objects.create_user(**data)

    def remove(self, user_id: int) -> None:
        """Remove a user from the repository (soft delete)."""
        user = self.get_by_id(user_id)
        if user:
            user.is_active = False
            user.save()

    def update(self, user: CustomUser) -> None:
        """Update a user in the repository."""
        user.save()

    def get_by_id(self, user_id: int) -> CustomUser | None:
        """Get user by ID."""
        try:
            return CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return None

    def get_by_email(self, email: str) -> CustomUser | None:
        """Get user by email."""
        try:
            return CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return None

    def get_all(self, **filters) -> list[CustomUser]:
        """Get all users with optional filters."""
        queryset = CustomUser.objects.filter(is_active=True)

        if filters.get("role"):
            queryset = queryset.filter(role=filters["role"])

        if filters.get("search"):
            from django.db.models import Q

            query = filters["search"]
            queryset = queryset.filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(email__icontains=query)
            )

        if "is_staff" in filters:
            queryset = queryset.filter(is_staff=filters["is_staff"])

        return list(queryset)

    def filter(self, **criteria) -> list[CustomUser]:
        """Filter users by criteria."""
        return list(CustomUser.objects.filter(**criteria))

    def count(self, **filters) -> int:
        """Count users with optional filters."""
        queryset = CustomUser.objects.filter(is_active=True)

        if "role" in filters:
            queryset = queryset.filter(role=filters["role"])

        return queryset.count()

    def get_admins(self) -> list[CustomUser]:
        """Get all admin users."""
        return list(CustomUser.objects.filter(is_active=True, role="admin"))

    def get_project_managers(self) -> list[CustomUser]:
        """Get all project managers."""
        return list(CustomUser.objects.filter(is_active=True, role="project_manager"))

    def search_by_name(self, query: str) -> list[CustomUser]:
        """Search users by name or email."""
        from django.db.models import Q

        return list(
            CustomUser.objects.filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(email__icontains=query),
                is_active=True,
            )
        )

    def deactivate_user(self, user_id: int) -> None:
        """Deactivate a user account."""
        user = self.get_by_id(user_id)
        if user:
            user.is_active = False
            user.save()

    def activate_user(self, user_id: int) -> None:
        """Activate a user account."""
        user = self.get_by_id(user_id)
        if user:
            user.is_active = True
            user.save()
