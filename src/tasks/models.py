"""Task domain models."""

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from src.projects.models import Project

CustomUser = get_user_model()


class TaskPriority(models.TextChoices):
    """Task priority choices."""

    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    CRITICAL = "critical", "Critical"


class TaskStatus(models.TextChoices):
    """Task status choices."""

    TODO = "to_do", "To Do"
    IN_PROGRESS = "in_progress", "In Progress"
    UNDER_REVIEW = "under_review", "Under Review"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class Task(models.Model):
    """
    Task domain model.
    Represents a task that belongs to a project.
    Implements Encapsulation with business logic.
    """

    # Identification
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Relationships
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    assigned_to = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="created_tasks",
    )

    # Status and priority
    status = models.CharField(max_length=20, choices=TaskStatus.choices, default=TaskStatus.TODO)
    priority = models.CharField(
        max_length=20, choices=TaskPriority.choices, default=TaskPriority.MEDIUM
    )

    # Dates
    due_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tasks_task"
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project", "status"]),
            models.Index(fields=["assigned_to"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["due_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.get_status_display()})"

    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if self.due_date and self.status != TaskStatus.COMPLETED:
            return self.due_date < timezone.localdate()
        return False

    def days_until_due(self) -> int | None:
        """Get days until task is due."""
        if self.due_date:
            delta = self.due_date - timezone.localdate()
            return delta.days
        return None

    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.status == TaskStatus.COMPLETED

    def mark_as_completed(self) -> None:
        """Mark task as completed."""
        if not self.is_completed():
            self.status = TaskStatus.COMPLETED
            self.completed_at = timezone.now()
            self.save()

    def can_be_completed(self) -> bool:
        """Check if task can be marked as completed."""
        return self.status != TaskStatus.CANCELLED

    def get_comment_count(self) -> int:
        """Get count of comments on this task."""
        return self.comments.count()

    def is_assigned(self) -> bool:
        """Check if task is assigned to someone."""
        return self.assigned_to is not None

    def get_priority_color(self) -> str:
        """Get color based on priority."""
        colors = {
            TaskPriority.LOW: "green",
            TaskPriority.MEDIUM: "blue",
            TaskPriority.HIGH: "orange",
            TaskPriority.CRITICAL: "red",
        }
        return colors.get(TaskPriority(self.priority), "blue")


class TaskComment(models.Model):
    """
    Task comment model.
    Allows users to comment on tasks.
    Implements activity tracking.
    """

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="task_comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tasks_taskcomment"
        verbose_name = "Task Comment"
        verbose_name_plural = "Task Comments"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["task", "created_at"]),
            models.Index(fields=["author"]),
        ]

    def __str__(self) -> str:
        return f"Comment by {self.author.email} on {self.task.title}"
