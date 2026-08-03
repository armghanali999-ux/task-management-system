"""
Dependency Injection Container and Factory.
Manages service instantiation and dependency resolution.
Follows Inversion of Control (IoC) principle.
"""

import inspect
from collections.abc import Callable
from typing import Any


class DIContainer:
    """
    Simple Dependency Injection Container.
    Supports singleton, factory, and transient lifetimes.
    """

    def __init__(self):
        self._services: dict[str, Any] = {}
        self._factories: dict[str, Callable] = {}
        self._singletons: dict[str, Any] = {}

    def register_singleton(self, service_name: str, service_class: type) -> None:
        """Register a singleton service (same instance every time)."""
        self._services[service_name] = {"class": service_class, "lifetime": "singleton"}

    def register_factory(self, service_name: str, factory_func: Callable) -> None:
        """Register a factory service (new instance every time)."""
        self._factories[service_name] = factory_func

    def register_transient(self, service_name: str, service_class: type) -> None:
        """Register a class that is rebuilt each time it is resolved."""
        self._services[service_name] = {"class": service_class, "lifetime": "transient"}

    def register_instance(self, service_name: str, instance: Any) -> None:
        """Register an existing instance."""
        self._singletons[service_name] = instance

    def resolve(self, service_name: str) -> Any:
        """Resolve a service from the container."""
        # Check if already resolved singleton
        if service_name in self._singletons:
            return self._singletons[service_name]

        # Check if factory
        if service_name in self._factories:
            return self._factories[service_name]()

        # Check if registered service
        if service_name in self._services:
            service_info = self._services[service_name]
            service_class = service_info["class"]

            # Resolve dependencies
            instance = self._instantiate_class(service_class)

            # Cache if singleton
            if service_info["lifetime"] == "singleton":
                self._singletons[service_name] = instance

            return instance

        raise ValueError(f"Service '{service_name}' not registered in DI container")

    def _instantiate_class(self, service_class: type) -> Any:
        """Instantiate a class with automatic dependency injection."""
        signature = inspect.signature(service_class)
        kwargs = {}

        for param_name, param in signature.parameters.items():
            if param_name == "self":
                continue

            # Try to resolve parameter from container
            if param_name in self._services or param_name in self._factories:
                kwargs[param_name] = self.resolve(param_name)
            elif param.default != inspect.Parameter.empty:
                kwargs[param_name] = param.default

        return service_class(**kwargs)


class ServiceFactory:
    """
    Service Factory for creating domain and application services.
    Implements Factory and Builder patterns.
    """

    def __init__(self, container: DIContainer | None = None):
        self.container = container or DIContainer()

    def create_service(self, service_class: type) -> Any:
        """Create a service with resolved dependencies."""
        return self.container._instantiate_class(service_class)

    @staticmethod
    def get_registered_services() -> dict[str, str]:
        """Get all registered services for introspection."""
        return {
            "user_repository": "UserRepository",
            "project_repository": "ProjectRepository",
            "task_repository": "TaskRepository",
            "comment_repository": "CommentRepository",
            "activity_repository": "ActivityRepository",
        }
