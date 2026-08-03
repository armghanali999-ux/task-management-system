"""Project application services."""

from typing import Any

from django.contrib.auth import get_user_model
from django.utils.text import slugify

from src.activity.events import publish_activity
from src.activity.models import ActivityType
from src.projects.models import Project, ProjectStatus
from src.projects.repositories import ProjectRepository
from src.shared.domain import ApplicationService
from src.shared.utils import (
    BusinessRuleException,
    EntityNotFoundException,
    PermissionDeniedException,
    log_operation,
)

CustomUser = get_user_model()


class CreateProjectService(ApplicationService):
    """Service for creating a new project."""

    def __init__(self, project_repository: ProjectRepository | None = None):
        self.project_repository = project_repository or ProjectRepository()

    @log_operation("Create Project")
    def execute(
        self,
        title: str,
        owner_id: int,
        description: str = "",
        start_date=None,
        end_date=None,
    ) -> dict[str, Any]:
        """Create a new project."""
        # Check if owner exists
        try:
            owner = CustomUser.objects.get(id=owner_id)
        except CustomUser.DoesNotExist:
            raise EntityNotFoundException(f"Owner with id {owner_id} not found")

        # Create project with slug
        slug = slugify(title)
        # Ensure slug is unique
        count = 1
        original_slug = slug
        while Project.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{count}"
            count += 1

        project = Project(
            title=title,
            slug=slug,
            description=description,
            owner=owner,
            status=ProjectStatus.PLANNED,
            start_date=start_date,
            end_date=end_date,
        )

        self.project_repository.add(project)
        publish_activity(
            owner.id,
            ActivityType.PROJECT_CREATED,
            project,
            f"Project '{project.title}' created",
        )

        return {
            "id": project.id,
            "title": project.title,
            "slug": project.slug,
            "status": project.status,
        }


class UpdateProjectService(ApplicationService):
    """Service for updating a project."""

    def __init__(self, project_repository: ProjectRepository | None = None):
        self.project_repository = project_repository or ProjectRepository()

    @log_operation("Update Project")
    def execute(self, project_id: int, requesting_user_id: int, **kwargs) -> Project:
        """Update a project."""
        project = self.project_repository.get_by_id(project_id)

        if not project:
            raise EntityNotFoundException(f"Project with id {project_id} not found")

        # Check authorization
        if (
            project.owner_id != requesting_user_id
            and not CustomUser.objects.get(id=requesting_user_id).is_admin()
        ):
            raise PermissionDeniedException("You do not have permission to update this project")

        # Update allowed fields
        allowed_fields = ["title", "description", "status", "start_date", "end_date"]
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(project, field, value)

        self.project_repository.update(project)
        return project


class DeleteProjectService(ApplicationService):
    """Service for deleting a project."""

    def __init__(self, project_repository: ProjectRepository | None = None):
        self.project_repository = project_repository or ProjectRepository()

    @log_operation("Delete Project")
    def execute(self, project_id: int, requesting_user_id: int) -> dict[str, str]:
        """Delete a project."""
        project = self.project_repository.get_by_id(project_id)

        if not project:
            raise EntityNotFoundException(f"Project with id {project_id} not found")

        # Check authorization - only owner can delete
        if project.owner_id != requesting_user_id:
            raise PermissionDeniedException("Only the project owner can delete the project")

        self.project_repository.remove(project_id)
        return {"message": "Project deleted successfully"}


class AddProjectMemberService(ApplicationService):
    """Service for adding members to a project."""

    def __init__(self, project_repository: ProjectRepository | None = None):
        self.project_repository = project_repository or ProjectRepository()

    @log_operation("Add Project Member")
    def execute(self, project_id: int, user_id: int, role: str = "member") -> dict[str, Any]:
        """Add a member to a project."""
        project = self.project_repository.get_by_id(project_id)

        if not project:
            raise EntityNotFoundException(f"Project with id {project_id} not found")

        if not project.can_add_members():
            raise BusinessRuleException("Cannot add members to a completed project")

        # Check if user exists
        try:
            CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise EntityNotFoundException(f"User with id {user_id} not found")

        self.project_repository.add_member(project_id, user_id, role)

        return {
            "project_id": project_id,
            "user_id": user_id,
            "role": role,
            "message": "Member added to project",
        }


class ListProjectsService(ApplicationService):
    """Service for listing projects."""

    def __init__(self, project_repository: ProjectRepository | None = None):
        self.project_repository = project_repository or ProjectRepository()

    @log_operation("List Projects")
    def execute(self, **filters) -> list[Project]:
        """Get list of projects with optional filters."""
        return self.project_repository.get_all(**filters)
