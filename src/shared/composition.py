"""Application composition root.

This is the only module responsible for wiring concrete repositories to
application services. Views resolve use cases by name and remain unaware of
constructor details.
"""

from functools import lru_cache

from src.projects.repositories import ProjectRepository
from src.projects.services import (
    AddProjectMemberService,
    CreateProjectService,
    DeleteProjectService,
    ListProjectsService,
    UpdateProjectService,
)
from src.shared.dashboard import DashboardService
from src.shared.di_container import DIContainer
from src.tasks.repositories import TaskCommentRepository, TaskRepository
from src.tasks.services import (
    AddTaskCommentService,
    AssignTaskService,
    CreateTaskService,
    UpdateTaskService,
)
from src.users.repositories import UserRepository
from src.users.services import (
    UserAuthenticationService,
    UserListService,
    UserProfileUpdateService,
    UserRegistrationService,
)


@lru_cache(maxsize=1)
def get_container() -> DIContainer:
    """Build and cache the process-wide dependency graph."""
    container = DIContainer()
    container.register_singleton("user_repository", UserRepository)
    container.register_singleton("project_repository", ProjectRepository)
    container.register_singleton("task_repository", TaskRepository)
    container.register_singleton("comment_repository", TaskCommentRepository)

    bindings = {
        "user_registration_service": UserRegistrationService,
        "user_authentication_service": UserAuthenticationService,
        "user_profile_update_service": UserProfileUpdateService,
        "user_list_service": UserListService,
        "create_project_service": CreateProjectService,
        "update_project_service": UpdateProjectService,
        "delete_project_service": DeleteProjectService,
        "add_project_member_service": AddProjectMemberService,
        "list_projects_service": ListProjectsService,
        "create_task_service": CreateTaskService,
        "update_task_service": UpdateTaskService,
        "assign_task_service": AssignTaskService,
        "add_task_comment_service": AddTaskCommentService,
        "dashboard_service": DashboardService,
    }
    for name, service in bindings.items():
        container.register_transient(name, service)
    return container


def resolve(name: str):
    """Resolve an application dependency from the composition root."""
    return get_container().resolve(name)
