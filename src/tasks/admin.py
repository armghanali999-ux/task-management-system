"""Task app admin configuration."""

from django.contrib import admin

from src.tasks.models import Task, TaskComment


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin for Task model."""

    list_display = ("title", "project", "status", "priority", "assigned_to", "due_date")
    list_filter = ("status", "priority", "due_date", "created_at")
    search_fields = ("title", "description", "project__title")
    readonly_fields = ("created_at", "updated_at", "completed_at")
    fieldsets = (
        ("Task Info", {"fields": ("title", "description", "project")}),
        ("Status", {"fields": ("status", "priority")}),
        ("Assignment", {"fields": ("assigned_to", "created_by")}),
        ("Dates", {"fields": ("start_date", "due_date", "completed_at")}),
        ("Metadata", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    """Admin for TaskComment model."""

    list_display = ("task", "author", "created_at")
    list_filter = ("created_at", "task")
    search_fields = ("content", "task__title", "author__email")
    readonly_fields = ("created_at", "updated_at")
