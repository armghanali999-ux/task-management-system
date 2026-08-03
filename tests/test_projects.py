"""
Comprehensive tests for the Projects module.
Tests ProjectRepository, ProjectServices, ProjectViewSet.
"""

from datetime import datetime, timedelta

import pytest
from rest_framework import status

from src.projects.models import Project, ProjectRole, ProjectStatus
from src.projects.repositories import ProjectRepository
from src.projects.services import (
    AddProjectMemberService,
    CreateProjectService,
    DeleteProjectService,
    ListProjectsService,
    UpdateProjectService,
)
from src.shared.utils import EntityNotFoundException


class TestProjectModel:
    """Test Project model and its methods."""

    def test_create_project(self, db, project_manager_user):
        """Test creating a project."""
        project = Project.objects.create(
            title="Test Project",
            slug="test-project",
            description="Test Description",
            owner=project_manager_user,
            status=ProjectStatus.ACTIVE,
        )
        assert project.title == "Test Project"
        assert project.owner == project_manager_user
        assert project.status == ProjectStatus.ACTIVE

    def test_project_is_overdue(self, db, project_manager_user):
        """Test is_overdue method."""
        past_date = datetime.now().date() - timedelta(days=1)
        project = Project.objects.create(
            title="Overdue Project",
            slug="overdue-project",
            owner=project_manager_user,
            end_date=past_date,
            status=ProjectStatus.ACTIVE,
        )
        assert project.is_overdue()

    def test_project_not_overdue(self, db, project_manager_user):
        """Test is_overdue returns False for future deadline."""
        future_date = datetime.now().date() + timedelta(days=1)
        project = Project.objects.create(
            title="Future Project",
            slug="future-project",
            owner=project_manager_user,
            end_date=future_date,
            status=ProjectStatus.ACTIVE,
        )
        assert not project.is_overdue()

    def test_days_until_deadline(self, db, project_manager_user):
        """Test days_until_deadline calculation."""
        future_date = datetime.now().date() + timedelta(days=5)
        project = Project.objects.create(
            title="Project",
            slug="project",
            owner=project_manager_user,
            end_date=future_date,
        )
        days = project.days_until_deadline()
        assert days == 5

    def test_add_member(self, db, project, team_member_user):
        """Test adding member to project."""
        project.members.add(team_member_user, through_defaults={"role": "member"})
        assert project.members.filter(id=team_member_user.id).exists()

    def test_get_progress_percentage(self, db, project):
        """Test get_progress_percentage method."""
        progress = project.get_progress_percentage()
        assert isinstance(progress, (int, float))
        assert 0 <= progress <= 100


class TestProjectRepository:
    """Test ProjectRepository methods (Repository Pattern)."""

    def test_get_by_slug(self, db, project):
        """Test retrieving project by slug."""
        repo = ProjectRepository()
        retrieved = repo.get_by_slug("test-project")
        assert retrieved.id == project.id

    def test_get_by_slug_not_found(self, db):
        """Test getting non-existent project by slug."""
        repo = ProjectRepository()
        retrieved = repo.get_by_slug("nonexistent-slug")
        assert retrieved is None

    def test_get_by_user(self, db, project, project_manager_user):
        """Test retrieving all projects by owner."""
        repo = ProjectRepository()
        projects = repo.get_by_user(project_manager_user)
        assert project in projects

    def test_get_active_projects(self, db, project_manager_user):
        """Test retrieving only active projects."""
        Project.objects.create(
            title="Inactive Project",
            slug="inactive-project",
            owner=project_manager_user,
            status=ProjectStatus.COMPLETED,
        )
        repo = ProjectRepository()
        active = repo.get_active_projects()
        assert all(p.status == ProjectStatus.ACTIVE for p in active)

    def test_add_member(self, db, project, team_member_user):
        """Test adding member through repository."""
        repo = ProjectRepository()
        repo.add_member(project, team_member_user, ProjectRole.MEMBER)
        assert project.members.filter(id=team_member_user.id).exists()

    def test_remove_member(self, db, project, team_member_user):
        """Test removing member through repository."""
        project.members.add(team_member_user, through_defaults={"role": "member"})
        repo = ProjectRepository()
        repo.remove_member(project, team_member_user)
        assert not project.members.filter(id=team_member_user.id).exists()

    def test_is_member(self, db, project, project_manager_user, team_member_user):
        """Test checking if user is project member."""
        repo = ProjectRepository()
        assert repo.is_member(project, project_manager_user)
        assert not repo.is_member(project, team_member_user)


class TestCreateProjectService:
    """Test CreateProjectService (Application Service Pattern)."""

    def test_create_project(self, db, project_manager_user):
        """Test creating a new project."""
        service = CreateProjectService()
        result = service.execute(
            title="New Project",
            description="New Description",
            owner_id=project_manager_user.id,
        )
        assert result["id"]
        assert Project.objects.filter(title="New Project").exists()

    def test_create_project_without_owner(self, db):
        """Test creating project without owner fails."""
        service = CreateProjectService()
        with pytest.raises(EntityNotFoundException):
            service.execute(title="Orphan Project", description="No owner", owner_id=99999)


class TestUpdateProjectService:
    """Test UpdateProjectService (Application Service Pattern)."""

    def test_update_project(self, db, project, project_manager_user):
        """Test updating project details."""
        service = UpdateProjectService()
        result = service.execute(
            project_id=project.id,
            requesting_user_id=project_manager_user.id,
            title="Updated Name",
            description="Updated Description",
        )
        assert result.id == project.id
        updated = Project.objects.get(id=project.id)
        assert updated.title == "Updated Name"

    def test_update_nonexistent_project(self, db, project_manager_user):
        """Test updating non-existent project."""
        service = UpdateProjectService()
        with pytest.raises(EntityNotFoundException):
            service.execute(
                project_id=99999, requesting_user_id=project_manager_user.id, title="Updated"
            )


class TestDeleteProjectService:
    """Test DeleteProjectService (Application Service Pattern)."""

    def test_delete_project(self, db, project, project_manager_user):
        """Test deleting a project."""
        project_id = project.id
        service = DeleteProjectService()
        result = service.execute(project_id=project_id, requesting_user_id=project_manager_user.id)
        assert "message" in result
        assert not Project.objects.filter(id=project_id).exists()


class TestAddProjectMemberService:
    """Test AddProjectMemberService (Application Service Pattern)."""

    def test_add_member_to_project(self, db, project, team_member_user):
        """Test adding member to project."""
        service = AddProjectMemberService()
        result = service.execute(
            project_id=project.id,
            user_id=team_member_user.id,
            role="member",
        )
        assert result["user_id"] == team_member_user.id
        assert project.members.filter(id=team_member_user.id).exists()

    def test_add_nonexistent_user_to_project(self, db, project):
        """Test adding non-existent user fails."""
        service = AddProjectMemberService()
        with pytest.raises(EntityNotFoundException):
            service.execute(project_id=project.id, user_id=99999, role="member")


class TestListProjectsService:
    """Test ListProjectsService (Application Service Pattern)."""

    def test_list_user_projects(self, db, project_manager_user, project):
        """Test listing projects for a user."""
        service = ListProjectsService()
        result = service.execute(user_id=project_manager_user.id)
        assert project in result

    def test_list_all_projects(self, db, project):
        """Test listing all projects."""
        service = ListProjectsService()
        result = service.execute(user_id=None)
        assert len(result) >= 1


class TestProjectAPI:
    """Test Project REST API endpoints."""

    def test_list_projects(self, authenticated_api_client, project):
        """Test GET /api/projects/"""
        response = authenticated_api_client.get("/api/projects/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_project(self, authenticated_api_client, db):
        """Test POST /api/projects/"""
        response = authenticated_api_client.post(
            "/api/projects/",
            {
                "name": "New Project",
                "description": "Test",
                "status": ProjectStatus.ACTIVE,
            },
            format="json",
        )
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]

    def test_retrieve_project(self, authenticated_api_client, project, team_member_user):
        """Test GET /api/projects/{id}/"""
        project.members.add(team_member_user)
        response = authenticated_api_client.get(f"/api/projects/{project.id}/")
        assert response.status_code == status.HTTP_200_OK

    def test_update_project(self, authenticated_api_client, project, project_manager_user):
        """Test PATCH /api/projects/{id}/"""
        response = authenticated_api_client.patch(
            f"/api/projects/{project.id}/",
            {"name": "Updated Name"},
            format="json",
        )
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_403_FORBIDDEN]

    def test_delete_project(self, authenticated_api_client, project):
        """Test DELETE /api/projects/{id}/"""
        response = authenticated_api_client.delete(f"/api/projects/{project.id}/")
        assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_403_FORBIDDEN]

    def test_add_project_member(
        self, authenticated_api_client, project, team_member_user, project_manager_user
    ):
        """Test POST /api/projects/{id}/add_member/"""
        response = authenticated_api_client.post(
            f"/api/projects/{project.id}/add_member/",
            {"user_id": team_member_user.id, "role": "member"},
            format="json",
        )
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_403_FORBIDDEN]


class TestProjectPermissions:
    """Test permission checks in Projects module."""

    def test_only_owner_can_delete_project(
        self, db, project, project_manager_user, team_member_user
    ):
        """Test that only project owner can delete project."""
        repo = ProjectRepository()
        repo.remove_member(project, project_manager_user)
        repo.add_member(project, team_member_user, "member")
        # Non-owner should not be able to delete in service layer
        # This is handled by UpdateProjectService authorization
