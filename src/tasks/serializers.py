"""Task serializers."""

from rest_framework import serializers

from src.tasks.models import Task, TaskComment
from src.users.serializers import UserListSerializer


class TaskCommentSerializer(serializers.ModelSerializer):
    """Serializer for task comments."""

    author = UserListSerializer(read_only=True)

    class Meta:
        model = TaskComment
        fields = ["id", "task_id", "author", "content", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class TaskListSerializer(serializers.ModelSerializer):
    """Serializer for listing tasks."""

    assigned_to = UserListSerializer(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)
    is_overdue = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "status",
            "status_display",
            "priority",
            "priority_display",
            "assigned_to",
            "due_date",
            "is_overdue",
            "comment_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_is_overdue(self, obj):
        """Check if task is overdue."""
        return obj.is_overdue()

    def get_comment_count(self, obj):
        """Get comment count."""
        return obj.get_comment_count()


class TaskSerializer(serializers.ModelSerializer):
    """Full task serializer."""

    assigned_to = UserListSerializer(read_only=True)
    created_by = UserListSerializer(read_only=True)
    comments = TaskCommentSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)
    is_overdue = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()
    is_assigned = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "project_id",
            "status",
            "status_display",
            "priority",
            "priority_display",
            "assigned_to",
            "created_by",
            "due_date",
            "start_date",
            "completed_at",
            "is_overdue",
            "days_until_due",
            "is_assigned",
            "comments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "completed_at", "created_at", "updated_at"]

    def get_is_overdue(self, obj):
        """Check if task is overdue."""
        return obj.is_overdue()

    def get_days_until_due(self, obj):
        """Get days until due."""
        return obj.days_until_due()

    def get_is_assigned(self, obj):
        """Check if task is assigned."""
        return obj.is_assigned()


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating tasks."""

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "priority",
            "status",
            "due_date",
            "start_date",
            "assigned_to",
        ]
