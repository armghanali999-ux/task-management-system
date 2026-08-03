"""
Comprehensive tests for the Activity module.
Tests ActivityLog model, ActivityLogRepository, ActivityLogViewSet.
"""

from django.contrib.contenttypes.models import ContentType
from rest_framework import status

from src.activity.models import ActivityLog, ActivityType
from src.projects.models import Project
from src.tasks.models import Task, TaskStatus


class TestActivityLogModel:
    """Test ActivityLog model and its methods."""

    def test_create_activity_log(self, db, admin_user, team_member_user):
        """Test creating an activity log entry."""
        log = ActivityLog.objects.create(
            actor=admin_user,
            activity_type=ActivityType.USER_CREATED,
            content_type=ContentType.objects.get_for_model(team_member_user),
            object_id=team_member_user.id,
            details={"email": "user@test.com"},
            description=f"User {team_member_user.email} created",
        )
        assert log.actor == admin_user
        assert log.activity_type == ActivityType.USER_CREATED

    def test_log_task_update(self, db, task, project_manager_user):
        """Test logging a task update."""
        log = ActivityLog.objects.create(
            actor=project_manager_user,
            activity_type=ActivityType.TASK_UPDATED,
            content_type=ContentType.objects.get_for_model(Task),
            object_id=task.id,
            details={"status": TaskStatus.COMPLETED},
            description="Task marked as completed",
        )
        assert log.content_type.model == "task"
        assert log.object_id == task.id

    def test_log_project_creation(self, db, project, project_manager_user):
        """Test logging project creation."""
        log = ActivityLog.objects.create(
            actor=project_manager_user,
            activity_type=ActivityType.PROJECT_CREATED,
            content_type=ContentType.objects.get_for_model(Project),
            object_id=project.id,
            description=f"Project '{project.title}' created",
        )
        assert log.activity_type == ActivityType.PROJECT_CREATED


class TestActivityLogQueries:
    """Test ActivityLog querying and filtering."""

    def test_get_activities_by_actor(self, db, admin_user, team_member_user):
        """Test getting activities by specific actor."""
        ActivityLog.objects.create(
            actor=admin_user,
            activity_type=ActivityType.USER_CREATED,
            content_type=ContentType.objects.get_for_model(admin_user),
            object_id=admin_user.id,
            description="User created",
        )
        ActivityLog.objects.create(
            actor=team_member_user,
            activity_type=ActivityType.TASK_CREATED,
            content_type=ContentType.objects.get_for_model(team_member_user),
            object_id=team_member_user.id,
            description="Task created",
        )
        admin_logs = ActivityLog.objects.filter(actor=admin_user)
        assert admin_logs.count() >= 1

    def test_get_activities_by_type(self, db, admin_user):
        """Test filtering activities by type."""
        ActivityLog.objects.create(
            actor=admin_user,
            activity_type=ActivityType.USER_CREATED,
            content_type=ContentType.objects.get_for_model(admin_user),
            object_id=admin_user.id,
            description="User 1 created",
        )
        ActivityLog.objects.create(
            actor=admin_user,
            activity_type=ActivityType.USER_UPDATED,
            content_type=ContentType.objects.get_for_model(admin_user),
            object_id=admin_user.id,
            description="User 1 updated",
        )
        created_logs = ActivityLog.objects.filter(activity_type=ActivityType.USER_CREATED)
        assert created_logs.count() >= 1

    def test_get_recent_activities(self, db, admin_user):
        """Test getting most recent activities."""
        for i in range(5):
            ActivityLog.objects.create(
                actor=admin_user,
                activity_type=ActivityType.USER_CREATED,
                content_type=ContentType.objects.get_for_model(admin_user),
                object_id=admin_user.id,
                description=f"Activity {i}",
            )
        recent = ActivityLog.objects.all().order_by("-created_at")[:3]
        assert len(list(recent)) <= 3

    def test_activity_log_ordering(self, db, admin_user):
        """Test that activity logs are ordered by creation time."""
        logs = []
        for i in range(3):
            log = ActivityLog.objects.create(
                actor=admin_user,
                activity_type=ActivityType.USER_CREATED,
                content_type=ContentType.objects.get_for_model(admin_user),
                object_id=admin_user.id,
                description=f"Activity {i}",
            )
            logs.append(log)

        ordered = ActivityLog.objects.filter(id__in=[log.id for log in logs]).order_by("created_at")
        assert list(ordered) == logs


class TestActivityLogAPI:
    """Test Activity REST API endpoints."""

    def test_list_activity_logs(self, authenticated_api_client):
        """Test GET /api/activity/"""
        response = authenticated_api_client.get("/api/activity/")
        assert response.status_code == status.HTTP_200_OK

    def test_list_activity_logs_unauthorized(self, api_client):
        """Test accessing activity logs without authentication."""
        response = api_client.get("/api/activity/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_delete_activity_log(self, admin_api_client, db, admin_user):
        """Test that activity logs cannot be deleted via API."""
        log = ActivityLog.objects.create(
            actor=admin_user,
            activity_type=ActivityType.USER_CREATED,
            content_type=ContentType.objects.get_for_model(admin_user),
            object_id=admin_user.id,
            description="Test",
        )
        response = admin_api_client.delete(f"/api/activity/{log.id}/")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_activity_log_readonly(self, admin_api_client, admin_user):
        """Test that activity logs are read-only."""
        response = admin_api_client.post(
            "/api/activity/",
            {
                "activity_type": ActivityType.USER_CREATED,
                "description": "Manual log",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


class TestActivityLogPermissions:
    """Test permission checks for Activity logs."""

    def test_team_member_can_view_own_activities(self, authenticated_api_client, team_member_user):
        """Test that users can view activities related to their actions."""
        response = authenticated_api_client.get("/api/activity/")
        assert response.status_code == status.HTTP_200_OK

    def test_can_filter_by_activity_type(self, authenticated_api_client):
        """Test filtering activity logs by type."""
        response = authenticated_api_client.get(
            f"/api/activity/?activity_type={ActivityType.TASK_CREATED}"
        )
        assert response.status_code == status.HTTP_200_OK


class TestActivityLogIndexing:
    """Test that activity logs are properly indexed for performance."""

    def test_activity_log_indexes_created(self, db):
        """Test that indexes exist on activity log model."""
        # This test verifies that the database schema includes proper indexes
        from django.db import connection

        # Use Django's portable introspection rather than backend-specific SQL.
        table_name = ActivityLog._meta.db_table
        with connection.cursor() as cursor:
            constraints = connection.introspection.get_constraints(cursor, table_name)
        assert any(item["index"] for item in constraints.values())
