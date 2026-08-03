"""Project serializers."""

from rest_framework import serializers

from src.projects.models import Project, ProjectMember
from src.users.serializers import UserListSerializer


class ProjectMemberSerializer(serializers.ModelSerializer):
    """Serializer for ProjectMember."""

    user = UserListSerializer(read_only=True)

    class Meta:
        model = ProjectMember
        fields = ["id", "user", "role", "joined_at"]
        read_only_fields = ["id", "joined_at"]


class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer for listing projects."""

    owner = UserListSerializer(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    task_count = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "slug",
            "status",
            "status_display",
            "owner",
            "start_date",
            "end_date",
            "task_count",
            "progress",
            "created_at",
        ]
        read_only_fields = ["id", "slug", "created_at"]

    def get_task_count(self, obj):
        """Get task count."""
        return obj.get_task_count()

    def get_progress(self, obj):
        """Get progress percentage."""
        return obj.get_progress_percentage()


class ProjectSerializer(serializers.ModelSerializer):
    """Full project serializer."""

    owner = UserListSerializer(read_only=True)
    members = ProjectMemberSerializer(source="projectmember_set", many=True, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    task_count = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    days_until_deadline = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "status",
            "status_display",
            "owner",
            "members",
            "start_date",
            "end_date",
            "task_count",
            "progress",
            "is_overdue",
            "days_until_deadline",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]

    def get_task_count(self, obj):
        """Get task count."""
        return obj.get_task_count()

    def get_progress(self, obj):
        """Get progress percentage."""
        return obj.get_progress_percentage()

    def get_is_overdue(self, obj):
        """Check if project is overdue."""
        return obj.is_overdue()

    def get_days_until_deadline(self, obj):
        """Get days until deadline."""
        return obj.days_until_deadline()


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating projects."""

    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "status",
            "start_date",
            "end_date",
        ]
