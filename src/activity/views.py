"""Activity API views."""

from rest_framework import filters, permissions, viewsets

from src.activity.models import ActivityLog
from src.activity.serializers import ActivityLogSerializer


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only viewset for activity logs."""

    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering = ["-created_at"]
    search_fields = ["description", "activity_type"]

    def get_queryset(self):
        """Filter queryset based on user."""
        user = self.request.user
        if user.is_admin():
            return ActivityLog.objects.all()
        # Show activities for user's projects and tasks
        return ActivityLog.objects.filter(actor=user).order_by("-created_at")
