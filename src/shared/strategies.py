"""Production reporting strategies used by dashboard queries."""

from abc import ABC, abstractmethod

from django.db.models import QuerySet


class TaskScopeStrategy(ABC):
    """Strategy contract for selecting the tasks visible in a report."""

    @abstractmethod
    def select(self) -> QuerySet:
        """Return the task queryset for this reporting scope."""


class SystemTaskScopeStrategy(TaskScopeStrategy):
    """Select every task for an administrator report."""

    def select(self) -> QuerySet:
        from src.tasks.models import Task

        return Task.objects.all()


class UserTaskScopeStrategy(TaskScopeStrategy):
    """Select tasks visible to one user."""

    def __init__(self, user_id: int):
        self.user_id = user_id

    def select(self) -> QuerySet:
        from django.db.models import Q

        from src.tasks.models import Task

        return Task.objects.filter(
            Q(project__owner_id=self.user_id)
            | Q(project__projectmember__user_id=self.user_id)
            | Q(assigned_to_id=self.user_id)
        ).distinct()


class TaskScopeStrategyFactory:
    """Choose a reporting strategy from the requested dashboard scope."""

    @staticmethod
    def create(user_id: int | None) -> TaskScopeStrategy:
        return UserTaskScopeStrategy(user_id) if user_id else SystemTaskScopeStrategy()
