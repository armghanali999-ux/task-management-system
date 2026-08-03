"""
Dashboard services for analytics and reporting.
"""

from datetime import timedelta
from typing import Any

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone

from src.projects.models import Project, ProjectStatus
from src.shared.domain import ApplicationService
from src.shared.strategies import TaskScopeStrategyFactory
from src.tasks.models import Task, TaskStatus

CustomUser = get_user_model()


class DashboardService(ApplicationService):
    """
    Service for dashboard statistics and metrics.
    Implements analytics and reporting use case.
    """

    @staticmethod
    def execute(user_id: int | None = None, **kwargs) -> dict[str, Any]:
        """
        Get dashboard statistics.
        """
        today = timezone.now().date()
        one_week_ago = today - timedelta(days=7)

        # Base queries
        if user_id:
            # User-specific dashboard
            user = CustomUser.objects.get(id=user_id)
            projects = Project.objects.filter(
                Q(owner=user) | Q(projectmember__user=user)
            ).distinct()
            tasks = TaskScopeStrategyFactory.create(user_id).select()
        else:
            # Admin dashboard - all data
            projects = Project.objects.all()
            tasks = TaskScopeStrategyFactory.create(None).select()

        # Project statistics
        total_projects = projects.count()
        active_projects = projects.filter(status=ProjectStatus.ACTIVE).count()
        completed_projects = projects.filter(status=ProjectStatus.COMPLETED).count()
        overdue_projects = sum(1 for p in projects if p.is_overdue())

        # Task statistics
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status=TaskStatus.COMPLETED).count()
        in_progress_tasks = tasks.filter(status=TaskStatus.IN_PROGRESS).count()
        overdue_tasks = sum(1 for t in tasks if t.is_overdue())

        # Tasks by priority
        critical_tasks = (
            tasks.filter(priority="critical").exclude(status=TaskStatus.COMPLETED).count()
        )
        high_priority_tasks = (
            tasks.filter(priority="high").exclude(status=TaskStatus.COMPLETED).count()
        )

        # Tasks by status
        tasks_by_status = {
            "to_do": tasks.filter(status=TaskStatus.TODO).count(),
            "in_progress": tasks.filter(status=TaskStatus.IN_PROGRESS).count(),
            "under_review": tasks.filter(status=TaskStatus.UNDER_REVIEW).count(),
            "completed": tasks.filter(status=TaskStatus.COMPLETED).count(),
            "cancelled": tasks.filter(status=TaskStatus.CANCELLED).count(),
        }

        # Recent activity
        recent_completed_tasks = tasks.filter(
            status=TaskStatus.COMPLETED, completed_at__gte=one_week_ago
        ).count()

        # User-specific stats if applicable
        assigned_tasks_count = 0
        unassigned_tasks = 0
        if user_id:
            assigned_tasks_count = Task.objects.filter(assigned_to_id=user_id).count()
            unassigned_tasks = tasks.filter(assigned_to__isnull=True).count()

        return {
            "summary": {
                "total_projects": total_projects,
                "active_projects": active_projects,
                "completed_projects": completed_projects,
                "overdue_projects": overdue_projects,
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "in_progress_tasks": in_progress_tasks,
                "overdue_tasks": overdue_tasks,
                "critical_tasks": critical_tasks,
                "high_priority_tasks": high_priority_tasks,
            },
            "tasks_by_status": tasks_by_status,
            "recent_activity": {
                "tasks_completed_this_week": recent_completed_tasks,
            },
            "user_stats": (
                {
                    "assigned_tasks": assigned_tasks_count,
                    "unassigned_tasks": unassigned_tasks,
                }
                if user_id
                else None
            ),
            "timestamp": today.isoformat(),
        }
