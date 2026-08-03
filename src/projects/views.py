"""Project API views."""

from django.db import models
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from src.projects.models import Project
from src.projects.serializers import (
    ProjectCreateUpdateSerializer,
    ProjectListSerializer,
    ProjectMemberSerializer,
    ProjectSerializer,
)
from src.shared.composition import resolve
from src.shared.utils import EntityNotFoundException, PermissionDeniedException


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for Project management."""

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "slug"]
    ordering_fields = ["created_at", "start_date", "end_date"]
    ordering = ["-created_at"]

    repository = resolve("project_repository")

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return ProjectListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return ProjectCreateUpdateSerializer
        return self.serializer_class

    def get_queryset(self):
        """Filter queryset based on user permissions."""
        user = self.request.user
        if user.is_admin():
            return Project.objects.all()
        # Show projects user owns or is member of
        return Project.objects.filter(
            models.Q(owner=user) | models.Q(projectmember__user=user)
        ).distinct()

    def create(self, request, *args, **kwargs):
        """Create a new project."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            service = resolve("create_project_service")
            project_data = service.execute(
                title=serializer.validated_data["title"],
                owner_id=request.user.id,
                description=serializer.validated_data.get("description", ""),
                start_date=serializer.validated_data.get("start_date"),
                end_date=serializer.validated_data.get("end_date"),
            )

            project = self.repository.get_by_id(project_data["id"])
            return Response(
                ProjectSerializer(project).data,
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """Update a project."""
        project_id = kwargs.get("pk") or self.kwargs.get("id")
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            service = resolve("update_project_service")
            project = service.execute(project_id, request.user.id, **serializer.validated_data)
            return Response(
                ProjectSerializer(project).data,
                status=status.HTTP_200_OK,
            )
        except (EntityNotFoundException, PermissionDeniedException) as e:
            status_code = (
                status.HTTP_404_NOT_FOUND
                if isinstance(e, EntityNotFoundException)
                else status.HTTP_403_FORBIDDEN
            )
            return Response({"error": str(e)}, status=status_code)

    def destroy(self, request, *args, **kwargs):
        """Delete a project."""
        project_id = kwargs.get("pk") or self.kwargs.get("id")

        try:
            service = resolve("delete_project_service")
            result = service.execute(project_id, request.user.id)
            return Response(result, status=status.HTTP_204_NO_CONTENT)
        except (EntityNotFoundException, PermissionDeniedException) as e:
            status_code = (
                status.HTTP_404_NOT_FOUND
                if isinstance(e, EntityNotFoundException)
                else status.HTTP_403_FORBIDDEN
            )
            return Response({"error": str(e)}, status=status_code)

    @action(detail=True, methods=["get"])
    def members(self, request, pk=None):
        """Get project members."""
        try:
            members = self.repository.get_members(pk)
            serializer = ProjectMemberSerializer(members, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def add_member(self, request, pk=None):
        """Add a member to the project."""
        user_id = request.data.get("user_id")
        role = request.data.get("role", "member")

        try:
            service = resolve("add_project_member_service")
            result = service.execute(pk, user_id, role)
            return Response(result, status=status.HTTP_201_CREATED)
        except (EntityNotFoundException, Exception) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def remove_member(self, request, pk=None):
        """Remove a member from the project."""
        user_id = request.data.get("user_id")

        try:
            removed = self.repository.remove_member(pk, user_id)
            if removed:
                return Response(
                    {"message": "Member removed"},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"error": "Member not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
