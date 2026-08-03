"""
Pytest configuration and shared fixtures.
Provides fixtures for users, projects, tasks for use across all tests.
"""

import pytest
from django.test import Client
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from src.projects.models import Project, ProjectStatus
from src.tasks.models import Task, TaskComment, TaskPriority, TaskStatus
from src.users.models import CustomUser, UserProfile, UserRole


@pytest.fixture
def api_client():
    """Provide API client for REST API tests."""
    return APIClient()


@pytest.fixture
def client():
    """Provide Django test client."""
    return Client()


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    user = CustomUser.objects.create_user(
        email="admin@example.com",
        password="adminpass123",
        first_name="Admin",
        last_name="User",
        role=UserRole.ADMIN,
    )
    return user


@pytest.fixture
def project_manager_user(db):
    """Create a project manager user."""
    user = CustomUser.objects.create_user(
        email="pm@example.com",
        password="pmpass123",
        first_name="Project",
        last_name="Manager",
        role=UserRole.PROJECT_MANAGER,
    )
    return user


@pytest.fixture
def team_member_user(db):
    """Create a team member user."""
    user = CustomUser.objects.create_user(
        email="member@example.com",
        password="memberpass123",
        first_name="Team",
        last_name="Member",
        role=UserRole.TEAM_MEMBER,
    )
    return user


@pytest.fixture
def authenticated_api_client(api_client, team_member_user):
    """Provide API client authenticated as team member."""
    token, _ = Token.objects.get_or_create(user=team_member_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return api_client


@pytest.fixture
def admin_api_client(api_client, admin_user):
    """Provide API client authenticated as admin."""
    token, _ = Token.objects.get_or_create(user=admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return api_client


@pytest.fixture
def project(db, project_manager_user):
    """Create a project."""
    project = Project.objects.create(
        title="Test Project",
        slug="test-project",
        description="A test project",
        owner=project_manager_user,
        status=ProjectStatus.ACTIVE,
    )
    project.members.add(project_manager_user, through_defaults={"role": "manager"})
    return project


@pytest.fixture
def task(db, project, team_member_user, project_manager_user):
    """Create a task."""
    task = Task.objects.create(
        title="Test Task",
        description="A test task",
        project=project,
        created_by=project_manager_user,
        assigned_to=team_member_user,
        priority=TaskPriority.MEDIUM,
        status=TaskStatus.IN_PROGRESS,
    )
    return task


@pytest.fixture
def task_comment(db, task, team_member_user):
    """Create a task comment."""
    comment = TaskComment.objects.create(
        task=task,
        author=team_member_user,
        content="This is a test comment",
    )
    return comment


@pytest.fixture
def user_profile(db, team_member_user):
    """Get or create user profile."""
    profile, _ = UserProfile.objects.get_or_create(user=team_member_user)
    return profile


# ============================================================================
# SERVICE FIXTURES - Provide properly instantiated services with dependencies
# ============================================================================


@pytest.fixture
def user_repository():
    """Provide UserRepository instance."""
    from src.users.repositories import UserRepository

    return UserRepository()


@pytest.fixture
def project_repository():
    """Provide ProjectRepository instance."""
    from src.projects.repositories import ProjectRepository

    return ProjectRepository()


@pytest.fixture
def task_repository():
    """Provide TaskRepository instance."""
    from src.tasks.repositories import TaskRepository

    return TaskRepository()


@pytest.fixture
def task_comment_repository():
    """Provide TaskCommentRepository instance."""
    from src.tasks.repositories import TaskCommentRepository

    return TaskCommentRepository()


@pytest.fixture
def user_registration_service(user_repository):
    """Provide UserRegistrationService with injected repository."""
    from src.users.services import UserRegistrationService

    return UserRegistrationService(user_repository)


@pytest.fixture
def user_authentication_service(user_repository):
    """Provide UserAuthenticationService with injected repository."""
    from src.users.services import UserAuthenticationService

    return UserAuthenticationService(user_repository)


@pytest.fixture
def user_profile_update_service(user_repository):
    """Provide UserProfileUpdateService with injected repository."""
    from src.users.services import UserProfileUpdateService

    return UserProfileUpdateService(user_repository)


@pytest.fixture
def user_list_service(user_repository):
    """Provide UserListService with injected repository."""
    from src.users.services import UserListService

    return UserListService(user_repository)


@pytest.fixture
def user_deactivation_service(user_repository):
    """Provide UserDeactivationService with injected repository."""
    from src.users.services import UserDeactivationService

    return UserDeactivationService(user_repository)


@pytest.fixture
def create_project_service(project_repository, user_repository):
    """Provide CreateProjectService with injected repositories."""
    from src.projects.services import CreateProjectService

    return CreateProjectService(project_repository, user_repository)


@pytest.fixture
def update_project_service(project_repository, user_repository):
    """Provide UpdateProjectService with injected repositories."""
    from src.projects.services import UpdateProjectService

    return UpdateProjectService(project_repository, user_repository)


@pytest.fixture
def delete_project_service(project_repository, user_repository):
    """Provide DeleteProjectService with injected repositories."""
    from src.projects.services import DeleteProjectService

    return DeleteProjectService(project_repository, user_repository)


@pytest.fixture
def add_project_member_service(project_repository, user_repository):
    """Provide AddProjectMemberService with injected repositories."""
    from src.projects.services import AddProjectMemberService

    return AddProjectMemberService(project_repository, user_repository)


@pytest.fixture
def list_projects_service(project_repository):
    """Provide ListProjectsService with injected repository."""
    from src.projects.services import ListProjectsService

    return ListProjectsService(project_repository)


@pytest.fixture
def create_task_service(task_repository, project_repository, user_repository):
    """Provide CreateTaskService with injected repositories."""
    from src.tasks.services import CreateTaskService

    return CreateTaskService(task_repository, project_repository, user_repository)


@pytest.fixture
def update_task_service(task_repository, user_repository, project_repository):
    """Provide UpdateTaskService with injected repositories."""
    from src.tasks.services import UpdateTaskService

    return UpdateTaskService(task_repository, user_repository, project_repository)


@pytest.fixture
def assign_task_service(task_repository, user_repository):
    """Provide AssignTaskService with injected repositories."""
    from src.tasks.services import AssignTaskService

    return AssignTaskService(task_repository, user_repository)


@pytest.fixture
def add_task_comment_service(task_repository, task_comment_repository, user_repository):
    """Provide AddTaskCommentService with injected repositories."""
    from src.tasks.services import AddTaskCommentService

    return AddTaskCommentService(task_repository, task_comment_repository, user_repository)


@pytest.fixture
def dashboard_service():
    """Provide DashboardService."""
    from src.shared.dashboard import DashboardService

    return DashboardService()
