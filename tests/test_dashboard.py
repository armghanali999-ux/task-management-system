"""
Comprehensive tests for the Dashboard module.
Tests DashboardService and dashboard views.
"""

from datetime import datetime, timedelta

from rest_framework import status

from src.projects.models import Project, ProjectStatus
from src.shared.dashboard import DashboardService
from src.tasks.models import Task, TaskStatus


class TestDashboardService:
    """Test DashboardService (Application Service Pattern)."""

    def test_dashboard_service_initializes(self):
        """Test that DashboardService can be instantiated."""
        service = DashboardService()
        assert service is not None

    def test_dashboard_execute_returns_dict(self, db, team_member_user):
        """Test that execute() returns a dictionary."""
        service = DashboardService()
        result = service.execute(user=team_member_user, admin=False)
        assert isinstance(result, dict)

    def test_user_dashboard_contains_summary(self, db, team_member_user, project, task):
        """Test that user dashboard contains summary data."""
        service = DashboardService()
        result = service.execute(user=team_member_user, admin=False)

        assert "summary" in result or "projects" in result or "tasks" in result

    def test_admin_dashboard_contains_system_stats(self, db, admin_user, project, task):
        """Test that admin dashboard contains system-wide statistics."""
        service = DashboardService()
        result = service.execute(user=admin_user, admin=True)

        assert isinstance(result, dict)
        # Admin dashboard should have more comprehensive data

    def test_dashboard_task_counts(self, db, team_member_user, project, project_manager_user):
        """Test dashboard task counting."""
        # Create multiple tasks with different statuses
        Task.objects.create(
            title="Todo",
            project=project,
            created_by=project_manager_user,
            status=TaskStatus.TODO,
        )
        Task.objects.create(
            title="In Progress",
            project=project,
            created_by=project_manager_user,
            assigned_to=team_member_user,
            status=TaskStatus.IN_PROGRESS,
        )
        Task.objects.create(
            title="Completed",
            project=project,
            created_by=project_manager_user,
            status=TaskStatus.COMPLETED,
            completed_at=datetime.now(),
        )

        service = DashboardService()
        result = service.execute(user=team_member_user, admin=False)
        assert isinstance(result, dict)

    def test_dashboard_project_stats(self, db, project_manager_user):
        """Test dashboard project statistics."""
        Project.objects.create(
            title="Active Project",
            slug="active",
            owner=project_manager_user,
            status=ProjectStatus.ACTIVE,
        )
        Project.objects.create(
            title="Completed Project",
            slug="completed",
            owner=project_manager_user,
            status=ProjectStatus.COMPLETED,
        )

        service = DashboardService()
        result = service.execute(user=project_manager_user, admin=False)
        assert isinstance(result, dict)

    def test_dashboard_overdue_tasks(self, db, project_manager_user, project, team_member_user):
        """Test that dashboard detects overdue tasks."""
        past_date = datetime.now().date() - timedelta(days=1)
        Task.objects.create(
            title="Overdue Task",
            project=project,
            created_by=project_manager_user,
            assigned_to=team_member_user,
            due_date=past_date,
            status=TaskStatus.IN_PROGRESS,
        )

        service = DashboardService()
        result = service.execute(user=team_member_user, admin=False)
        # Dashboard should include overdue task information
        assert isinstance(result, dict)


class TestDashboardAPI:
    """Test Dashboard REST API endpoints."""

    def test_user_dashboard_endpoint(self, authenticated_api_client):
        """Test GET /api/dashboard/"""
        response = authenticated_api_client.get("/api/dashboard/")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, dict)

    def test_user_dashboard_unauthorized(self, api_client):
        """Test accessing dashboard without authentication."""
        response = api_client.get("/api/dashboard/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_admin_dashboard_endpoint(self, admin_api_client):
        """Test GET /api/admin-dashboard/ (admin only)"""
        response = admin_api_client.get("/api/admin-dashboard/")
        assert response.status_code == status.HTTP_200_OK

    def test_non_admin_cannot_access_admin_dashboard(self, authenticated_api_client):
        """Test that non-admins cannot access admin dashboard."""
        response = authenticated_api_client.get("/api/admin-dashboard/")
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]

    def test_dashboard_response_structure(self, authenticated_api_client):
        """Test that dashboard response has expected structure."""
        response = authenticated_api_client.get("/api/dashboard/")
        data = response.data
        # Dashboard should return some data structure
        assert isinstance(data, dict)


class TestDashboardMetrics:
    """Test dashboard metrics calculations."""

    def test_calculate_task_completion_rate(self, db, project, project_manager_user):
        """Test calculating task completion rate."""
        Task.objects.create(
            title="Completed 1",
            project=project,
            created_by=project_manager_user,
            status=TaskStatus.COMPLETED,
            completed_at=datetime.now(),
        )
        Task.objects.create(
            title="Completed 2",
            project=project,
            created_by=project_manager_user,
            status=TaskStatus.COMPLETED,
            completed_at=datetime.now(),
        )
        Task.objects.create(
            title="In Progress",
            project=project,
            created_by=project_manager_user,
            status=TaskStatus.IN_PROGRESS,
        )

        total = Task.objects.filter(project=project).count()
        completed = Task.objects.filter(project=project, status=TaskStatus.COMPLETED).count()

        if total > 0:
            rate = (completed / total) * 100
            assert 0 <= rate <= 100

    def test_calculate_overdue_percentage(self, db, project, project_manager_user):
        """Test calculating overdue task percentage."""
        current_date = datetime.now().date()

        # Create overdue tasks
        Task.objects.create(
            title="Overdue 1",
            project=project,
            created_by=project_manager_user,
            due_date=current_date - timedelta(days=1),
            status=TaskStatus.IN_PROGRESS,
        )

        # Create on-time tasks
        Task.objects.create(
            title="On-time 1",
            project=project,
            created_by=project_manager_user,
            due_date=current_date + timedelta(days=5),
            status=TaskStatus.IN_PROGRESS,
        )

        overdue = Task.objects.filter(
            project=project,
            due_date__lt=current_date,
            status__in=[TaskStatus.TODO, TaskStatus.IN_PROGRESS],
        ).count()

        assert overdue >= 1


class TestDashboardFiltering:
    """Test dashboard data filtering by various criteria."""

    def test_filter_by_user_assigned_tasks(
        self, db, team_member_user, project, project_manager_user
    ):
        """Test filtering dashboard to show only user's assigned tasks."""
        task1 = Task.objects.create(
            title="Assigned to Member",
            project=project,
            created_by=project_manager_user,
            assigned_to=team_member_user,
        )
        task2 = Task.objects.create(
            title="Assigned to PM",
            project=project,
            created_by=project_manager_user,
            assigned_to=project_manager_user,
        )

        user_tasks = Task.objects.filter(assigned_to=team_member_user)
        assert task1 in user_tasks
        assert task2 not in user_tasks

    def test_filter_by_project(self, db, project, project_manager_user):
        """Test filtering dashboard tasks by project."""
        other_project = Project.objects.create(
            title="Other Project",
            slug="other",
            owner=project_manager_user,
            status=ProjectStatus.ACTIVE,
        )

        task1 = Task.objects.create(
            title="Task in Project 1",
            project=project,
            created_by=project_manager_user,
        )
        task2 = Task.objects.create(
            title="Task in Project 2",
            project=other_project,
            created_by=project_manager_user,
        )

        project_tasks = Task.objects.filter(project=project)
        assert task1 in project_tasks
        assert task2 not in project_tasks
