"""Project app admin configuration."""

from django.contrib import admin

from src.projects.models import Project, ProjectMember


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin for Project model."""

    list_display = ("title", "status", "owner", "start_date", "end_date")
    list_filter = ("status", "created_at", "owner")
    search_fields = ("title", "slug", "description")
    readonly_fields = ("slug", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    """Admin for ProjectMember model."""

    list_display = ("project", "user", "role", "joined_at")
    list_filter = ("role", "joined_at", "project")
    search_fields = ("project__title", "user__email")
