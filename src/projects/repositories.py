"""Project domain repository."""

from src.projects.models import Project, ProjectMember
from src.shared.domain import Repository


class ProjectRepository(Repository):
    """Repository for Project model."""

    def add(self, project: Project) -> None:
        """Add a new project."""
        project.save()

    def create(self, data):
        return Project.objects.create(**data)

    def remove(self, project_id: int) -> None:
        """Remove (delete) a project."""
        try:
            project = Project.objects.get(id=project_id)
            project.delete()
        except Project.DoesNotExist:
            pass

    def update(self, project: Project) -> None:
        """Update a project."""
        project.save()

    def get_by_id(self, project_id: int) -> Project | None:
        """Get project by ID."""
        try:
            return Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return None

    def get_by_slug(self, slug: str) -> Project | None:
        """Get project by slug."""
        try:
            return Project.objects.get(slug=slug)
        except Project.DoesNotExist:
            return None

    def get_all(self, **filters) -> list[Project]:
        """Get all projects with optional filters."""
        queryset = Project.objects.all()

        if "status" in filters:
            queryset = queryset.filter(status=filters["status"])

        if "owner_id" in filters:
            queryset = queryset.filter(owner_id=filters["owner_id"])

        return list(queryset)

    def filter(self, **criteria) -> list[Project]:
        """Filter projects by criteria."""
        return list(Project.objects.filter(**criteria))

    def count(self, **filters) -> int:
        """Count projects."""
        queryset = Project.objects.all()

        if "status" in filters:
            queryset = queryset.filter(status=filters["status"])

        return queryset.count()

    def get_by_user(self, user_id: int) -> list[Project]:
        """Get all projects for a user (owned or member)."""
        from django.db.models import Q

        user_id = getattr(user_id, "pk", user_id)
        return list(
            Project.objects.filter(
                Q(owner_id=user_id) | Q(projectmember__user_id=user_id)
            ).distinct()
        )

    def get_active_projects(self) -> list[Project]:
        """Get all active projects."""
        return list(Project.objects.filter(status="active"))

    def get_overdue_projects(self) -> list[Project]:
        """Get all overdue projects."""

        return [p for p in Project.objects.all() if p.is_overdue()]

    def add_member(self, project_id: int, user_id: int, role: str = "member") -> ProjectMember:
        """Add a member to a project."""
        project_id = getattr(project_id, "pk", project_id)
        user_id = getattr(user_id, "pk", user_id)
        member, created = ProjectMember.objects.get_or_create(
            project_id=project_id,
            user_id=user_id,
            defaults={"role": role},
        )
        return member

    def remove_member(self, project_id: int, user_id: int) -> bool:
        """Remove a member from a project."""
        project_id = getattr(project_id, "pk", project_id)
        user_id = getattr(user_id, "pk", user_id)
        try:
            member = ProjectMember.objects.get(project_id=project_id, user_id=user_id)
            member.delete()
            return True
        except ProjectMember.DoesNotExist:
            return False

    def get_members(self, project_id: int) -> list[ProjectMember]:
        """Get all members of a project."""
        return list(ProjectMember.objects.filter(project_id=project_id))

    def is_member(self, project_id: int, user_id: int) -> bool:
        """Check if user is a member of the project."""
        project_id = getattr(project_id, "pk", project_id)
        user_id = getattr(user_id, "pk", user_id)
        return ProjectMember.objects.filter(project_id=project_id, user_id=user_id).exists()
