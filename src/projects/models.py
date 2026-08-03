"""Project domain models."""

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

CustomUser = get_user_model()


class ProjectStatus(models.TextChoices):
    """Project status choices."""

    PLANNED = "planned", "Planned"
    ACTIVE = "active", "Active"
    ON_HOLD = "on_hold", "On Hold"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class ProjectRole(models.TextChoices):
    """Roles available to members within a project."""

    OWNER = "owner", "Owner"
    MANAGER = "manager", "Manager"
    MEMBER = "member", "Member"


class Project(models.Model):
    """
    Project domain model.
    Represents a project that contains tasks.
    Implements Encapsulation with business logic methods.
    """

    # Identification
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, db_index=True)
    description = models.TextField(blank=True)

    # Status and dates
    status = models.CharField(
        max_length=20, choices=ProjectStatus.choices, default=ProjectStatus.PLANNED
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)  # Deadline

    # Owner and team
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="owned_projects",
    )
    members = models.ManyToManyField(
        CustomUser,
        related_name="projects",
        through="ProjectMember",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "projects_project"
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["status"]),
            models.Index(fields=["owner"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.get_status_display()})"

    def is_overdue(self) -> bool:
        """Check if project is overdue."""
        if self.end_date and self.status != ProjectStatus.COMPLETED:
            return self.end_date < timezone.localdate()
        return False

    def days_until_deadline(self) -> int | None:
        """Get days until project deadline."""
        if self.end_date:
            delta = self.end_date - timezone.localdate()
            return delta.days
        return None

    def is_active(self) -> bool:
        """Check if project is currently active."""
        return self.status == ProjectStatus.ACTIVE

    def can_add_members(self) -> bool:
        """Check if members can be added to this project."""
        return self.status != ProjectStatus.COMPLETED

    def get_task_count(self) -> int:
        """Get count of tasks in this project."""
        return self.tasks.count()

    def get_completed_task_count(self) -> int:
        """Get count of completed tasks."""
        return self.tasks.filter(status="completed").count()

    def get_progress_percentage(self) -> int:
        """Get project completion percentage."""
        total_tasks = self.get_task_count()
        if total_tasks == 0:
            return 0
        completed = self.get_completed_task_count()
        return int((completed / total_tasks) * 100)


class ProjectMember(models.Model):
    """
    Project membership model.
    Manages who is part of a project and their role.
    Implements many-to-many relationship with additional data.
    """

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ProjectRole.choices, default=ProjectRole.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "projects_projectmember"
        unique_together = ("project", "user")
        verbose_name = "Project Member"
        verbose_name_plural = "Project Members"

    def __str__(self) -> str:
        return f"{self.user.email} - {self.project.title} ({self.role})"

    def is_manager(self) -> bool:
        """Check if member has manager role."""
        return self.role in ["owner", "manager"]

    def can_edit_project(self) -> bool:
        """Check if member can edit project."""
        return self.role in ["owner", "manager"]

    def can_invite_members(self) -> bool:
        """Check if member can invite others."""
        return self.role in ["owner", "manager"]
