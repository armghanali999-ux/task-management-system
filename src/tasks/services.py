"""Task application services."""

from typing import Any

from django.contrib.auth import get_user_model
from django.utils import timezone

from src.activity.events import publish_activity
from src.activity.models import ActivityType
from src.projects.models import Project
from src.shared.domain import ApplicationService
from src.shared.utils import (
    BusinessRuleException,
    EntityNotFoundException,
    PermissionDeniedException,
    log_operation,
)
from src.tasks.models import Task, TaskComment, TaskStatus
from src.tasks.repositories import TaskCommentRepository, TaskRepository

CustomUser = get_user_model()


class CreateTaskService(ApplicationService):
    """Service for creating a new task."""

    def __init__(self, task_repository: TaskRepository | None = None):
        self.task_repository = task_repository or TaskRepository()

    @log_operation("Create Task")
    def execute(
        self,
        title: str,
        project_id: int,
        created_by_id: int,
        description: str = "",
        priority: str = "medium",
        due_date=None,
        assigned_to_id: int | None = None,
    ) -> dict[str, Any]:
        """Create a new task."""
        # Check if project exists
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise EntityNotFoundException(f"Project with id {project_id} not found")

        # Check if user exists
        try:
            created_by = CustomUser.objects.get(id=created_by_id)
        except CustomUser.DoesNotExist:
            raise EntityNotFoundException(f"User with id {created_by_id} not found")

        # Verify assigned_to exists if provided
        assigned_to = None
        if assigned_to_id:
            try:
                assigned_to = CustomUser.objects.get(id=assigned_to_id)
            except CustomUser.DoesNotExist:
                raise EntityNotFoundException(f"Assigned user with id {assigned_to_id} not found")

        # Create task
        task = Task(
            title=title,
            description=description,
            project=project,
            created_by=created_by,
            assigned_to=assigned_to,
            priority=priority,
            due_date=due_date,
        )

        self.task_repository.add(task)
        publish_activity(
            created_by.id,
            ActivityType.TASK_CREATED,
            task,
            f"Task '{task.title}' created",
        )

        return {
            "id": task.id,
            "title": task.title,
            "status": task.status,
            "priority": task.priority,
        }


class UpdateTaskService(ApplicationService):
    """Service for updating a task."""

    def __init__(self, task_repository: TaskRepository | None = None):
        self.task_repository = task_repository or TaskRepository()

    @log_operation("Update Task")
    def execute(self, task_id: int, requesting_user_id: int, **kwargs) -> Task:
        """Update a task."""
        task = self.task_repository.get_by_id(task_id)

        if not task:
            raise EntityNotFoundException(f"Task with id {task_id} not found")

        # Check authorization
        is_project_member = task.project.projectmember_set.filter(
            user_id=requesting_user_id
        ).exists()
        is_task_creator = task.created_by_id == requesting_user_id
        is_task_assigned = task.assigned_to_id == requesting_user_id
        is_admin = CustomUser.objects.get(id=requesting_user_id).is_admin()

        if not (is_project_member or is_task_creator or is_task_assigned or is_admin):
            raise PermissionDeniedException("You do not have permission to update this task")

        # Update allowed fields
        allowed_fields = [
            "title",
            "description",
            "status",
            "priority",
            "due_date",
            "assigned_to_id",
            "start_date",
        ]
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(task, field, value)

        # If marking as completed
        if kwargs.get("status") == TaskStatus.COMPLETED and not task.completed_at:
            task.completed_at = timezone.now()

        self.task_repository.update(task)
        return task


class AssignTaskService(ApplicationService):
    """Service for assigning tasks to users."""

    def __init__(self, task_repository: TaskRepository | None = None):
        self.task_repository = task_repository or TaskRepository()

    @log_operation("Assign Task")
    def execute(self, task_id: int, assigned_to_id: int) -> Task:
        """Assign a task to a user."""
        task = self.task_repository.get_by_id(task_id)

        if not task:
            raise EntityNotFoundException(f"Task with id {task_id} not found")

        # Check if user exists
        try:
            user = CustomUser.objects.get(id=assigned_to_id)
        except CustomUser.DoesNotExist:
            raise EntityNotFoundException(f"User with id {assigned_to_id} not found")

        # Verify user is project member
        is_member = task.project.projectmember_set.filter(user_id=assigned_to_id).exists()
        if not is_member and user != task.project.owner:
            raise BusinessRuleException("User is not a member of the project")

        task.assigned_to = user
        self.task_repository.update(task)
        return task


class AddTaskCommentService(ApplicationService):
    """Service for adding comments to tasks."""

    def __init__(self, comment_repository: TaskCommentRepository | None = None):
        self.comment_repository = comment_repository or TaskCommentRepository()

    @log_operation("Add Task Comment")
    def execute(self, task_id: int, author_id: int, content: str) -> TaskComment:
        """Add a comment to a task."""
        # Check if task exists
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise EntityNotFoundException(f"Task with id {task_id} not found")

        # Check if user exists
        try:
            author = CustomUser.objects.get(id=author_id)
        except CustomUser.DoesNotExist:
            raise EntityNotFoundException(f"User with id {author_id} not found")

        # Create comment
        comment = TaskComment(task=task, author=author, content=content)
        self.comment_repository.add(comment)
        publish_activity(
            author.id,
            ActivityType.COMMENTED,
            task,
            f"Comment added to task '{task.title}'",
            {"comment_id": comment.id},
        )
        return comment
