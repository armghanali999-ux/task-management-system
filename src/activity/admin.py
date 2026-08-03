"""Activity app admin configuration."""

from django.contrib import admin

from src.activity.models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    """Admin for ActivityLog model."""

    list_display = ("actor", "activity_type", "description", "created_at")
    list_filter = ("activity_type", "created_at", "actor")
    search_fields = ("description", "actor__email")
    readonly_fields = ("created_at", "actor", "activity_type", "content_type", "object_id")
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        """Prevent manual addition of activity logs."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of activity logs."""
        return False
