"""
User domain models.
Follows Clean Architecture with domain layer containing business logic.
"""

from typing import cast

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import EmailValidator
from django.db import models


class CustomUserManager(BaseUserManager):
    """Custom user manager for CustomUser model."""

    def create_user(self, email: str, password: str, **extra_fields) -> CustomUser:
        """Create and save a regular user."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = cast(CustomUser, self.model(email=email, **extra_fields))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, **extra_fields) -> CustomUser:
        """Create and save a superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class UserRole(models.TextChoices):
    """User role choices."""

    ADMIN = "admin", "Administrator"
    PROJECT_MANAGER = "project_manager", "Project Manager"
    TEAM_MEMBER = "team_member", "Team Member"


class CustomUser(AbstractUser):
    """
    Custom user model with email as primary identifier.
    Implements Encapsulation principle - data and behavior together.
    """

    # Override username - use email instead
    username = None
    email = models.EmailField(unique=True, validators=[EmailValidator()], max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.URLField(blank=True, null=True, help_text="URL to user avatar image")
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.TEAM_MEMBER)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    class Meta:
        db_table = "users_customuser"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.email} ({self.get_full_name()})"

    def get_full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def is_admin(self) -> bool:
        """Check if user is an administrator."""
        return self.role == UserRole.ADMIN or self.is_superuser

    def is_project_manager(self) -> bool:
        """Check if user is a project manager."""
        return self.role == UserRole.PROJECT_MANAGER

    def can_manage_users(self) -> bool:
        """Check if user can manage other users."""
        return self.is_admin() or self.is_project_manager()

    def can_view_reports(self) -> bool:
        """Check if user can view reports."""
        return self.is_admin() or self.is_project_manager()

    @property
    def display_name(self) -> str:
        """Get display name for the user."""
        full_name = self.get_full_name()
        return full_name if full_name != self.email else self.email.split("@")[0]


class UserProfile(models.Model):
    """Extended user profile for additional information."""

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="profile")
    department = models.CharField(max_length=100, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    preferred_language = models.CharField(max_length=10, default="en-us")
    theme_preference = models.CharField(
        max_length=20, choices=[("light", "Light"), ("dark", "Dark")], default="light"
    )
    notifications_enabled = models.BooleanField(default=True)
    two_factor_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users_userprofile"
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self) -> str:
        return f"Profile for {self.user.email}"
