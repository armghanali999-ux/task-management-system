"""Activity serializers."""

from rest_framework import serializers

from src.activity.models import ActivityLog
from src.users.serializers import UserListSerializer


class ActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for ActivityLog model."""

    actor = UserListSerializer(read_only=True)
    activity_type_display = serializers.CharField(
        source="get_activity_type_display", read_only=True
    )
    content_type_display = serializers.SerializerMethodField()

    class Meta:
        model = ActivityLog
        fields = [
            "id",
            "actor",
            "activity_type",
            "activity_type_display",
            "description",
            "details",
            "content_type_display",
            "object_id",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_content_type_display(self, obj):
        """Get content type display name."""
        return obj.content_type.name if obj.content_type else ""
