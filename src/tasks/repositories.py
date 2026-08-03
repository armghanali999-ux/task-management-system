"""Task repositories."""

from django.db.models import Q

from src.shared.domain import Repository
from src.tasks.models import Task, TaskComment


class TaskRepository(Repository):
    """Repository for Task model."""

    def add(self, task: Task) -> None:
        """Add a new task."""
        task.save()

    def create(self, data):
        return Task.objects.create(**data)

    def remove(self, task_id: int) -> None:
        """Remove (delete) a task."""
        try:
            task = Task.objects.get(id=task_id)
            task.delete()
        except Task.DoesNotExist:
            pass

    def update(self, task: Task) -> None:
        """Update a task."""
        task.save()

    def get_by_id(self, task_id: int) -> Task | None:
        """Get task by ID."""
        try:
            return Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return None

    def get_all(self, **filters) -> list[Task]:
        """Get all tasks with optional filters."""
        queryset = Task.objects.all()

        if "project_id" in filters:
            queryset = queryset.filter(project_id=filters["project_id"])

        if "assigned_to_id" in filters:
            queryset = queryset.filter(assigned_to_id=filters["assigned_to_id"])

        if "status" in filters:
            queryset = queryset.filter(status=filters["status"])

        if "priority" in filters:
            queryset = queryset.filter(priority=filters["priority"])

        return list(queryset)

    def filter(self, **criteria) -> list[Task]:
        """Filter tasks by criteria."""
        return list(Task.objects.filter(**criteria))

    def count(self, **filters) -> int:
        """Count tasks."""
        queryset = Task.objects.all()

        if "project_id" in filters:
            queryset = queryset.filter(project_id=filters["project_id"])

        if "status" in filters:
            queryset = queryset.filter(status=filters["status"])

        return queryset.count()

    def get_by_project(self, project_id: int) -> list[Task]:
        """Get all tasks in a project."""
        return list(Task.objects.filter(project_id=project_id))

    def get_assigned_to_user(self, user_id: int) -> list[Task]:
        """Get all tasks assigned to a user."""
        return list(Task.objects.filter(assigned_to_id=user_id))

    def get_overdue_tasks(self) -> list[Task]:
        """Get all overdue tasks."""
        return [t for t in Task.objects.all() if t.is_overdue()]

    def get_completed_tasks(self, project_id: int | None = None) -> list[Task]:
        """Get completed tasks, optionally filtered by project."""
        queryset = Task.objects.filter(status="completed")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return list(queryset)

    def get_tasks_by_status(self, status: str, project_id: int | None = None) -> list[Task]:
        """Get tasks by status, optionally filtered by project."""
        queryset = Task.objects.filter(status=status)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return list(queryset)

    def get_high_priority_tasks(self) -> list[Task]:
        """Get high priority tasks."""
        return list(
            Task.objects.filter(priority__in=["high", "critical"]).exclude(status="completed")
        )

    def search_tasks(self, query: str, project_id: int | None = None) -> list[Task]:
        """Search tasks by title or description."""
        queryset = Task.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return list(queryset)


class TaskCommentRepository(Repository):
    """Repository for TaskComment model."""

    def add(self, comment: TaskComment) -> None:
        """Add a new comment."""
        comment.save()

    def create(self, data):
        return TaskComment.objects.create(**data)

    def remove(self, comment_id: int) -> None:
        """Remove a comment."""
        try:
            comment = TaskComment.objects.get(id=comment_id)
            comment.delete()
        except TaskComment.DoesNotExist:
            pass

    def update(self, comment: TaskComment) -> None:
        """Update a comment."""
        comment.save()

    def get_by_id(self, comment_id: int) -> TaskComment | None:
        """Get comment by ID."""
        try:
            return TaskComment.objects.get(id=comment_id)
        except TaskComment.DoesNotExist:
            return None

    def get_all(self, **filters) -> list[TaskComment]:
        """Get all comments."""
        return list(TaskComment.objects.all())

    def filter(self, **criteria) -> list[TaskComment]:
        """Filter comments."""
        return list(TaskComment.objects.filter(**criteria))

    def count(self, **filters) -> int:
        """Count comments."""
        return TaskComment.objects.count()

    def get_task_comments(self, task_id: int) -> list[TaskComment]:
        """Get all comments for a task."""
        task_id = getattr(task_id, "pk", task_id)
        return list(TaskComment.objects.filter(task_id=task_id))

    def get_by_task(self, task_id: int) -> list[TaskComment]:
        """Readable alias for task-scoped comment retrieval."""
        return self.get_task_comments(task_id)

    def get_user_comments(self, user_id: int) -> list[TaskComment]:
        """Get all comments by a user."""
        return list(TaskComment.objects.filter(author_id=user_id))
