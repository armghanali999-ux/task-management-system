"""Task API views."""

from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from src.shared.composition import resolve
from src.shared.utils import EntityNotFoundException, PermissionDeniedException
from src.tasks.models import Task
from src.tasks.serializers import (
    TaskCommentSerializer,
    TaskCreateUpdateSerializer,
    TaskListSerializer,
    TaskSerializer,
)


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for Task management."""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "due_date", "priority"]
    ordering = ["-created_at"]

    repository = resolve("task_repository")

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return TaskListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return TaskCreateUpdateSerializer
        return self.serializer_class

    def get_queryset(self):
        """Filter queryset based on user permissions."""
        user = self.request.user
        if user.is_admin():
            return Task.objects.all()

        # Show tasks from projects user is part of
        from django.db.models import Q

        return Task.objects.filter(
            Q(project__owner=user) | Q(project__projectmember__user=user) | Q(assigned_to=user)
        ).distinct()

    def create(self, request, *args, **kwargs):
        """Create a new task."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            service = resolve("create_task_service")
            task_data = service.execute(
                title=serializer.validated_data["title"],
                project_id=request.data.get("project_id"),
                created_by_id=request.user.id,
                description=serializer.validated_data.get("description", ""),
                priority=serializer.validated_data.get("priority", "medium"),
                due_date=serializer.validated_data.get("due_date"),
                assigned_to_id=serializer.validated_data.get("assigned_to"),
            )

            task = self.repository.get_by_id(task_data["id"])
            return Response(
                TaskSerializer(task).data,
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """Update a task."""
        task_id = kwargs.get("pk")
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            service = resolve("update_task_service")
            task = service.execute(task_id, request.user.id, **serializer.validated_data)
            return Response(
                TaskSerializer(task).data,
                status=status.HTTP_200_OK,
            )
        except (EntityNotFoundException, PermissionDeniedException) as e:
            status_code = (
                status.HTTP_404_NOT_FOUND
                if isinstance(e, EntityNotFoundException)
                else status.HTTP_403_FORBIDDEN
            )
            return Response({"error": str(e)}, status=status_code)

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        """Assign task to a user."""
        user_id = request.data.get("user_id")

        try:
            service = resolve("assign_task_service")
            task = service.execute(pk, user_id)
            return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def comments(self, request, pk=None):
        """Get task comments."""
        try:
            comment_repository = resolve("comment_repository")
            comments = comment_repository.get_task_comments(pk)
            serializer = TaskCommentSerializer(comments, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def add_comment(self, request, pk=None):
        """Add comment to task."""
        content = request.data.get("content")

        if not content:
            return Response(
                {"error": "Content is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            service = resolve("add_task_comment_service")
            comment = service.execute(pk, request.user.id, content)
            return Response(
                TaskCommentSerializer(comment).data,
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def mark_completed(self, request, pk=None):
        """Mark task as completed."""
        try:
            task = self.repository.get_by_id(pk)
            if not task:
                return Response(
                    {"error": "Task not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            task.mark_as_completed()
            return Response(
                TaskSerializer(task).data,
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
