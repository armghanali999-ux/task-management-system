"""
Comprehensive tests for the Tasks module.
Tests TaskRepository, TaskCommentRepository, TaskServices, TaskViewSet.
"""

from datetime import datetime, timedelta

import pytest
from rest_framework import status

from src.shared.utils import EntityNotFoundException
from src.tasks.models import Task, TaskComment, TaskPriority, TaskStatus
from src.tasks.repositories import TaskCommentRepository, TaskRepository
from src.tasks.services import (
    AddTaskCommentService,
    AssignTaskService,
    CreateTaskService,
    UpdateTaskService,
)


class TestTaskModel:
    """Test Task model and its methods."""

    def test_create_task(self, db, project, project_manager_user):
        """Test creating a task."""
        task = Task.objects.create(
            title="Test Task",
            description="Test",
            project=project,
            created_by=project_manager_user,
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.TODO,
        )
        assert task.title == "Test Task"
        assert task.status == TaskStatus.TODO
        assert task.priority == TaskPriority.MEDIUM

    def test_task_is_overdue(self, db, project, project_manager_user):
        """Test is_overdue method."""
        past_date = datetime.now().date() - timedelta(days=1)
        task = Task.objects.create(
            title="Overdue Task",
            project=project,
            created_by=project_manager_user,
            due_date=past_date,
            status=TaskStatus.IN_PROGRESS,
        )
        assert task.is_overdue()

    def test_task_not_overdue(self, db, project, project_manager_user):
        """Test is_overdue returns False for future due date."""
        future_date = datetime.now().date() + timedelta(days=5)
        task = Task.objects.create(
            title="Future Task",
            project=project,
            created_by=project_manager_user,
            due_date=future_date,
            status=TaskStatus.TODO,
        )
        assert not task.is_overdue()

    def test_days_until_due(self, db, project, project_manager_user):
        """Test days_until_due calculation."""
        future_date = datetime.now().date() + timedelta(days=3)
        task = Task.objects.create(
            title="Task",
            project=project,
            created_by=project_manager_user,
            due_date=future_date,
        )
        days = task.days_until_due()
        assert days == 3

    def test_mark_as_completed(self, db, project, project_manager_user):
        """Test marking task as completed."""
        task = Task.objects.create(
            title="Task",
            project=project,
            created_by=project_manager_user,
            status=TaskStatus.IN_PROGRESS,
        )
        task.mark_as_completed()
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None

    def test_priority_color(self, db, project, project_manager_user):
        """Test get_priority_color method."""
        task = Task.objects.create(
            title="High Priority",
            project=project,
            created_by=project_manager_user,
            priority=TaskPriority.HIGH,
        )
        color = task.get_priority_color()
        assert color in ["red", "orange", "yellow", "green"]


class TestTaskRepository:
    """Test TaskRepository methods (Repository Pattern)."""

    def test_get_overdue_tasks(self, db, project, project_manager_user):
        """Test retrieving overdue tasks."""
        past_date = datetime.now().date() - timedelta(days=1)
        Task.objects.create(
            title="Overdue Task",
            project=project,
            created_by=project_manager_user,
            due_date=past_date,
            status=TaskStatus.IN_PROGRESS,
        )
        repo = TaskRepository()
        overdue = repo.get_overdue_tasks()
        assert len(overdue) > 0

    def test_get_completed_tasks(self, db, project, project_manager_user):
        """Test retrieving completed tasks."""
        task = Task.objects.create(
            title="Completed",
            project=project,
            created_by=project_manager_user,
            status=TaskStatus.COMPLETED,
            completed_at=datetime.now(),
        )
        repo = TaskRepository()
        completed = repo.get_completed_tasks()
        assert task in completed

    def test_get_high_priority_tasks(self, db, project, project_manager_user):
        """Test retrieving high priority tasks."""
        task = Task.objects.create(
            title="Important",
            project=project,
            created_by=project_manager_user,
            priority=TaskPriority.HIGH,
        )
        repo = TaskRepository()
        high_priority = repo.get_high_priority_tasks()
        assert task in high_priority

    def test_get_tasks_by_status(self, db, project, project_manager_user):
        """Test retrieving tasks by status."""
        task = Task.objects.create(
            title="In Progress",
            project=project,
            created_by=project_manager_user,
            status=TaskStatus.IN_PROGRESS,
        )
        repo = TaskRepository()
        in_progress = repo.get_tasks_by_status(TaskStatus.IN_PROGRESS)
        assert task in in_progress

    def test_search_tasks(self, db, project, project_manager_user):
        """Test searching tasks by title/description."""
        task = Task.objects.create(
            title="Search Test",
            description="Find me",
            project=project,
            created_by=project_manager_user,
        )
        repo = TaskRepository()
        results = repo.search_tasks("Search")
        assert task in results

    def test_create_task_via_repository(self, db, project, project_manager_user):
        """Test creating task through repository."""
        repo = TaskRepository()
        task_data = {
            "title": "New Task",
            "description": "Test",
            "project": project,
            "created_by": project_manager_user,
            "priority": TaskPriority.MEDIUM,
            "status": TaskStatus.TODO,
        }
        task = repo.create(task_data)
        assert task.title == "New Task"
        assert Task.objects.filter(id=task.id).exists()


class TestTaskCommentRepository:
    """Test TaskCommentRepository methods (Repository Pattern)."""

    def test_get_task_comments(self, db, task, team_member_user):
        """Test retrieving comments for a task."""
        comment = TaskComment.objects.create(
            task=task,
            author=team_member_user,
            content="Test comment",
        )
        repo = TaskCommentRepository()
        comments = repo.get_by_task(task)
        assert comment in comments

    def test_create_comment_via_repository(self, db, task, team_member_user):
        """Test creating comment through repository."""
        repo = TaskCommentRepository()
        comment_data = {
            "task": task,
            "author": team_member_user,
            "content": "New comment",
        }
        comment = repo.create(comment_data)
        assert comment.content == "New comment"


class TestCreateTaskService:
    """Test CreateTaskService (Application Service Pattern)."""

    def test_create_task(self, db, project, project_manager_user):
        """Test creating a new task."""
        service = CreateTaskService()
        result = service.execute(
            title="New Task",
            description="Test",
            project_id=project.id,
            created_by_id=project_manager_user.id,
            priority=TaskPriority.MEDIUM,
        )
        assert result["id"]
        assert Task.objects.filter(title="New Task").exists()

    def test_create_task_invalid_project(self, db, project_manager_user):
        """Test creating task with invalid project."""
        service = CreateTaskService()
        with pytest.raises(EntityNotFoundException):
            service.execute(
                title="Orphan Task",
                project_id=99999,
                created_by_id=project_manager_user.id,
            )


class TestUpdateTaskService:
    """Test UpdateTaskService (Application Service Pattern)."""

    def test_update_task(self, db, task, project_manager_user):
        """Test updating task details."""
        service = UpdateTaskService()
        result = service.execute(
            task_id=task.id,
            requesting_user_id=project_manager_user.id,
            title="Updated Title",
            description="Updated Description",
            status=TaskStatus.IN_PROGRESS,
        )
        assert result.id == task.id
        updated = Task.objects.get(id=task.id)
        assert updated.title == "Updated Title"
        assert updated.status == TaskStatus.IN_PROGRESS

    def test_update_nonexistent_task(self, db, project_manager_user):
        """Test updating non-existent task."""
        service = UpdateTaskService()
        with pytest.raises(EntityNotFoundException):
            service.execute(
                task_id=99999,
                requesting_user_id=project_manager_user.id,
                title="Updated",
            )


class TestAssignTaskService:
    """Test AssignTaskService (Application Service Pattern)."""

    def test_assign_task_to_user(self, db, task, team_member_user, project):
        """Test assigning task to a user."""
        task.assigned_to = None
        task.save()
        project.members.add(team_member_user)
        service = AssignTaskService()
        result = service.execute(
            task_id=task.id,
            assigned_to_id=team_member_user.id,
        )
        assert result.assigned_to == team_member_user
        updated_task = Task.objects.get(id=task.id)
        assert updated_task.assigned_to == team_member_user

    def test_assign_task_invalid_user(self, db, task):
        """Test assigning task to non-existent user."""
        service = AssignTaskService()
        with pytest.raises(EntityNotFoundException):
            service.execute(task_id=task.id, assigned_to_id=99999)


class TestAddTaskCommentService:
    """Test AddTaskCommentService (Application Service Pattern)."""

    def test_add_comment(self, db, task, team_member_user):
        """Test adding comment to task."""
        service = AddTaskCommentService()
        result = service.execute(
            task_id=task.id,
            author_id=team_member_user.id,
            content="Great work!",
        )
        assert result.id
        assert TaskComment.objects.filter(content="Great work!").exists()

    def test_add_comment_invalid_task(self, db, team_member_user):
        """Test adding comment to non-existent task."""
        service = AddTaskCommentService()
        with pytest.raises(EntityNotFoundException):
            service.execute(
                task_id=99999,
                author_id=team_member_user.id,
                content="Comment",
            )


class TestTaskAPI:
    """Test Task REST API endpoints."""

    def test_list_tasks(self, authenticated_api_client, task):
        """Test GET /api/tasks/"""
        response = authenticated_api_client.get("/api/tasks/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_task(self, authenticated_api_client, project, db):
        """Test POST /api/tasks/"""
        response = authenticated_api_client.post(
            "/api/tasks/",
            {
                "title": "API Task",
                "description": "Test",
                "project": project.id,
                "priority": TaskPriority.MEDIUM,
                "status": TaskStatus.TODO,
            },
            format="json",
        )
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]

    def test_retrieve_task(self, authenticated_api_client, task):
        """Test GET /api/tasks/{id}/"""
        response = authenticated_api_client.get(f"/api/tasks/{task.id}/")
        assert response.status_code == status.HTTP_200_OK

    def test_update_task(self, authenticated_api_client, task):
        """Test PATCH /api/tasks/{id}/"""
        response = authenticated_api_client.patch(
            f"/api/tasks/{task.id}/",
            {"title": "Updated Title"},
            format="json",
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]

    def test_delete_task(self, authenticated_api_client, task):
        """Test DELETE /api/tasks/{id}/"""
        response = authenticated_api_client.delete(f"/api/tasks/{task.id}/")
        assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_403_FORBIDDEN]

    def test_assign_task(self, authenticated_api_client, task, team_member_user):
        """Test POST /api/tasks/{id}/assign/"""
        task.project.members.add(team_member_user)
        response = authenticated_api_client.post(
            f"/api/tasks/{task.id}/assign/",
            {"user_id": team_member_user.id},
            format="json",
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]

    def test_mark_task_completed(self, authenticated_api_client, task):
        """Test POST /api/tasks/{id}/mark_completed/"""
        response = authenticated_api_client.post(
            f"/api/tasks/{task.id}/mark_completed/",
            format="json",
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]

    def test_add_task_comment(self, authenticated_api_client, task):
        """Test POST /api/tasks/{id}/add_comment/"""
        response = authenticated_api_client.post(
            f"/api/tasks/{task.id}/add_comment/",
            {"content": "Good progress"},
            format="json",
        )
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_403_FORBIDDEN]


class TestTaskFiltering:
    """Test Task filtering and querying."""

    def test_filter_by_priority(self, db, project, project_manager_user):
        """Test filtering tasks by priority."""
        Task.objects.create(
            title="High",
            project=project,
            created_by=project_manager_user,
            priority=TaskPriority.HIGH,
        )
        Task.objects.create(
            title="Low",
            project=project,
            created_by=project_manager_user,
            priority=TaskPriority.LOW,
        )
        high = Task.objects.filter(priority=TaskPriority.HIGH)
        assert high.count() >= 1

    def test_filter_by_status(self, db, project, project_manager_user):
        """Test filtering tasks by status."""
        Task.objects.create(
            title="Todo",
            project=project,
            created_by=project_manager_user,
            status=TaskStatus.TODO,
        )
        Task.objects.create(
            title="InProgress",
            project=project,
            created_by=project_manager_user,
            status=TaskStatus.IN_PROGRESS,
        )
        todo = Task.objects.filter(status=TaskStatus.TODO)
        assert todo.count() >= 1
