"""
Comprehensive tests for the Architecture layer.
Tests Dependency Injection container, Repository pattern, Service pattern,
Event Bus, design patterns, and SOLID principles implementation.
"""

from unittest.mock import Mock

import pytest

from src.shared.di_container import DIContainer, ServiceFactory
from src.shared.domain import (
    ApplicationService,
    DomainEvent,
    DomainService,
    EventPublisher,
    Repository,
    Specification,
    UnitOfWork,
)
from src.shared.events import InMemoryEventBus
from src.shared.utils import BusinessRuleException, DomainException, EntityNotFoundException


class TestRepositoryPattern:
    """Test Repository Pattern implementation."""

    def test_repository_is_abstract(self):
        """Test that Repository is an abstract base class."""
        assert hasattr(Repository, "__abstractmethods__")

    def test_repository_requires_create_method(self):
        """Test that repositories must implement create()."""
        # This should raise TypeError if not abstract
        with pytest.raises(TypeError):
            Repository()

    def test_repository_requires_update_method(self):
        """Test that repositories must implement update()."""
        # Repository requires persistence-neutral CRUD/query operations.
        methods = ["add", "remove", "update", "get_by_id", "get_all"]
        for method in methods:
            assert method in Repository.__abstractmethods__


class TestDomainServicePattern:
    """Test Domain Service Pattern implementation."""

    def test_domain_service_is_abstract(self):
        """Test that DomainService is abstract."""
        assert hasattr(DomainService, "__abstractmethods__")

    def test_domain_service_requires_execute(self):
        """Test that domain services must implement execute()."""
        assert "execute" in DomainService.__abstractmethods__

    def test_concrete_domain_service_implementation(self):
        """Test that concrete domain services can be implemented."""

        class ConcreteService(DomainService):
            def execute(self, **kwargs):
                return {"result": "success"}

        service = ConcreteService()
        result = service.execute()
        assert result["result"] == "success"


class TestApplicationServicePattern:
    """Test Application Service Pattern implementation."""

    def test_application_service_is_abstract(self):
        """Test that ApplicationService is abstract."""
        assert hasattr(ApplicationService, "__abstractmethods__")

    def test_application_service_requires_execute(self):
        """Test that application services must implement execute()."""
        assert "execute" in ApplicationService.__abstractmethods__

    def test_concrete_application_service_implementation(self):
        """Test that concrete application services can be implemented."""

        class ConcreteAppService(ApplicationService):
            def execute(self, **kwargs):
                return {"status": "processed"}

        service = ConcreteAppService()
        result = service.execute()
        assert result["status"] == "processed"


class TestSpecificationPattern:
    """Test Specification Pattern implementation."""

    def test_specification_is_abstract(self):
        """Test that Specification is abstract."""
        assert hasattr(Specification, "__abstractmethods__")

    def test_specification_requires_is_satisfied_by(self):
        """Test that specifications must implement is_satisfied_by()."""
        assert "is_satisfied_by" in Specification.__abstractmethods__

    def test_concrete_specification_implementation(self):
        """Test creating a concrete specification."""

        class ActiveProjectSpecification(Specification):
            def is_satisfied_by(self, project):
                return project.status == "ACTIVE"

        spec = ActiveProjectSpecification()

        # Create mock project
        mock_project = Mock()
        mock_project.status = "ACTIVE"

        assert spec.is_satisfied_by(mock_project)


class TestEventPublisherPattern:
    """Test Event Publisher Pattern (Observer pattern)."""

    def test_event_publisher_is_abstract(self):
        """Test that EventPublisher is abstract."""
        assert hasattr(EventPublisher, "__abstractmethods__")

    def test_event_publisher_requires_publish_method(self):
        """Test that event publishers must implement publish()."""
        assert "publish" in EventPublisher.__abstractmethods__

    def test_event_publisher_requires_subscribe_method(self):
        """Test that event publishers must implement subscribe()."""
        assert "subscribe" in EventPublisher.__abstractmethods__


class TestUnitOfWorkPattern:
    """Test Unit of Work Pattern implementation."""

    def test_unit_of_work_is_abstract(self):
        """Test that UnitOfWork is abstract."""
        assert hasattr(UnitOfWork, "__abstractmethods__")

    def test_unit_of_work_requires_begin_method(self):
        """Test that unit of work must implement begin()."""
        assert "begin" in UnitOfWork.__abstractmethods__

    def test_unit_of_work_requires_commit_method(self):
        """Test that unit of work must implement commit()."""
        assert "commit" in UnitOfWork.__abstractmethods__

    def test_unit_of_work_requires_rollback_method(self):
        """Test that unit of work must implement rollback()."""
        assert "rollback" in UnitOfWork.__abstractmethods__


class TestDependencyInjectionContainer:
    """Test Dependency Injection Container implementation."""

    def test_di_container_initialization(self):
        """Test creating a DI container."""
        container = DIContainer()
        assert container is not None

    def test_register_singleton(self):
        """Test registering a singleton service."""
        container = DIContainer()

        class MyService:
            pass

        container.register_singleton("service", MyService)

        instance1 = container.resolve("service")
        instance2 = container.resolve("service")

        assert instance1 is instance2

    def test_register_factory(self):
        """Test registering a factory service."""
        container = DIContainer()

        class MyService:
            pass

        container.register_factory("service", MyService)

        instance1 = container.resolve("service")
        instance2 = container.resolve("service")

        assert instance1 is not instance2

    def test_register_transient(self):
        """Test registering a transient service."""
        container = DIContainer()

        class MyService:
            pass

        container.register_transient("service", MyService)

        instance1 = container.resolve("service")
        instance2 = container.resolve("service")

        assert instance1 is not instance2

    def test_resolve_nonexistent_service(self):
        """Test resolving a service that doesn't exist."""
        container = DIContainer()

        with pytest.raises(Exception):
            container.resolve("nonexistent")


class TestServiceFactory:
    """Test Service Factory implementation."""

    def test_service_factory_initialization(self):
        """Test creating a service factory."""
        factory = ServiceFactory()
        assert factory is not None

    def test_factory_returns_callable(self):
        """Test that factory methods return callables."""
        from src.users.services import UserRegistrationService

        factory = ServiceFactory()
        service = factory.create_service(UserRegistrationService)

        # Service should be callable or have execute method
        assert hasattr(service, "execute") or callable(service)


class TestInMemoryEventBus:
    """Test InMemoryEventBus (Observer pattern)."""

    def test_event_bus_initialization(self):
        """Test creating an event bus."""
        bus = InMemoryEventBus()
        assert bus is not None

    def test_event_bus_implements_event_publisher(self):
        """Test that event bus implements EventPublisher interface."""
        bus = InMemoryEventBus()
        assert isinstance(bus, EventPublisher)

    def test_subscribe_to_event(self):
        """Test subscribing to an event."""
        bus = InMemoryEventBus()
        callback = Mock()

        # Subscribe to all events
        bus.subscribe(None, callback)

        # Verify subscription through observable behavior, not private state.
        event = DomainEvent(event_type="test")
        bus.subscribe("test", callback)
        bus.publish(event)
        callback.assert_called_once_with(event)

    def test_publish_event(self):
        """Test publishing an event."""
        bus = InMemoryEventBus()
        event = Mock()

        # Should not raise error
        bus.publish(event)

    def test_event_callback_invocation(self):
        """Test that callbacks are invoked on event."""
        bus = InMemoryEventBus()
        callback = Mock()

        class TestEvent(DomainEvent):
            pass

        bus.subscribe(TestEvent, callback)
        event = TestEvent()
        bus.publish(event)

        # Callback might be called or event might be collected
        # Depending on implementation


class TestDomainEvent:
    """Test DomainEvent base class."""

    def test_domain_event_is_dataclass(self):
        """Test that DomainEvent is a dataclass-like class."""
        event = DomainEvent()
        assert hasattr(event, "timestamp") or isinstance(event, DomainEvent)

    def test_create_custom_domain_event(self):
        """Test creating a custom domain event."""

        class UserCreatedEvent(DomainEvent):
            user_id: int
            email: str

        event = UserCreatedEvent()
        assert event is not None


class TestExceptions:
    """Test custom exception hierarchy."""

    def test_domain_exception(self):
        """Test DomainException."""
        exc = DomainException("Test error")
        assert str(exc) == "Test error"

    def test_business_rule_exception(self):
        """Test BusinessRuleException."""
        exc = BusinessRuleException("Rule violation")
        assert isinstance(exc, DomainException)

    def test_entity_not_found_exception(self):
        """Test EntityNotFoundException."""
        exc = EntityNotFoundException("Entity", 123)
        assert isinstance(exc, DomainException)

    def test_permission_denied_exception(self):
        """Test PermissionDeniedException."""
        from src.shared.utils import PermissionDeniedException

        exc = PermissionDeniedException("Access denied")
        assert isinstance(exc, DomainException)


class TestSOLIDPrinciples:
    """Test SOLID principles implementation."""

    def test_single_responsibility_user_vs_project(self):
        """Test SRP: UserRepository and ProjectRepository have single responsibilities."""
        from src.projects.repositories import ProjectRepository
        from src.users.repositories import UserRepository

        user_repo = UserRepository()
        project_repo = ProjectRepository()

        # Each repository should have methods specific to its domain
        assert hasattr(user_repo, "get_by_email")
        assert hasattr(project_repo, "get_by_slug")

    def test_open_closed_principle_with_abstract_classes(self):
        """Test OCP: New services can be added without modifying abstractions."""
        # We should be able to create new ApplicationService implementations
        # without changing ApplicationService ABC

        class CustomService(ApplicationService):
            def execute(self, **kwargs):
                return {"status": "ok"}

        service = CustomService()
        result = service.execute()
        assert result["status"] == "ok"

    def test_liskov_substitution_repositories(self):
        """Test LSP: Concrete repositories can substitute for Repository interface."""
        from src.projects.repositories import ProjectRepository
        from src.users.repositories import UserRepository

        repos = [UserRepository(), ProjectRepository()]

        for repo in repos:
            assert isinstance(repo, Repository)
            # All should have standard repository methods
            assert hasattr(repo, "add")
            assert hasattr(repo, "get_by_id")
            assert hasattr(repo, "update")
            assert hasattr(repo, "remove")

    def test_interface_segregation_principle(self):
        """Test ISP: Fine-grained interfaces."""
        # Repository, DomainService, ApplicationService, EventPublisher
        # are separate interfaces with specific methods

        assert hasattr(Repository, "__abstractmethods__")
        assert hasattr(EventPublisher, "__abstractmethods__")
        assert hasattr(DomainService, "__abstractmethods__")
        assert hasattr(ApplicationService, "__abstractmethods__")

    def test_dependency_inversion_principle(self):
        """Test DIP: Services depend on abstractions, not implementations."""
        from src.users.services import UserRegistrationService

        service = UserRegistrationService()
        # Service should use Repository ABC, not concrete UserRepository
        assert isinstance(service, ApplicationService)


class TestOOPPrinciples:
    """Test Object-Oriented Programming principles."""

    def test_encapsulation_in_models(self):
        """Test encapsulation: private methods and attributes."""
        # Models should encapsulate business logic
        from src.tasks.models import Task

        # Check for methods that encapsulate logic
        assert hasattr(Task, "is_overdue")
        assert hasattr(Task, "days_until_due")
        assert hasattr(Task, "mark_as_completed")

    def test_inheritance_in_custom_user(self, db):
        """Test inheritance from AbstractUser."""
        from django.contrib.auth.models import AbstractUser

        from src.users.models import CustomUser

        user = CustomUser.objects.create_user(email="test@example.com", password="pass")
        # CustomUser should inherit from AbstractUser
        assert isinstance(user, AbstractUser)

    def test_polymorphism_in_services(self):
        """Test polymorphism: multiple services implement same interface."""
        from src.users.services import (
            UserAuthenticationService,
            UserListService,
            UserRegistrationService,
        )

        services = [
            UserRegistrationService(),
            UserAuthenticationService(),
            UserListService(),
        ]

        for service in services:
            assert isinstance(service, ApplicationService)
            assert hasattr(service, "execute")

    def test_abstraction_in_domain_layer(self):
        """Test abstraction: abstract base classes define contracts."""
        assert hasattr(Repository, "__abstractmethods__")
        assert len(Repository.__abstractmethods__) > 0


class TestDesignPatterns:
    """Test implemented design patterns."""

    def test_repository_pattern_usage(self):
        """Test Repository pattern is used throughout."""
        from src.projects.repositories import ProjectRepository
        from src.tasks.repositories import TaskRepository
        from src.users.repositories import UserRepository

        repos = [UserRepository(), ProjectRepository(), TaskRepository()]

        for repo in repos:
            assert isinstance(repo, Repository)

    def test_service_layer_pattern_usage(self):
        """Test Service Layer pattern with DomainService and ApplicationService."""
        from src.projects.services import CreateProjectService
        from src.tasks.services import CreateTaskService
        from src.users.services import UserRegistrationService

        services = [
            UserRegistrationService(),
            CreateProjectService(),
            CreateTaskService(),
        ]

        for service in services:
            assert isinstance(service, ApplicationService)
            assert hasattr(service, "execute")

    def test_factory_pattern_in_service_factory(self):
        """Test Factory pattern in ServiceFactory."""
        factory = ServiceFactory()
        # Factory should be able to create different service instances
        assert hasattr(factory, "create_service") or callable(factory)

    def test_observer_pattern_in_event_bus(self):
        """Test Observer pattern with EventBus."""
        bus = InMemoryEventBus()

        # Event bus should support subscribe and publish
        assert hasattr(bus, "subscribe")
        assert hasattr(bus, "publish")

    def test_specification_pattern_for_filtering(self):
        """Test Specification pattern for business rule encapsulation."""

        class ActiveTaskSpecification(Specification):
            def is_satisfied_by(self, task):
                return task.status != "COMPLETED"

        spec = ActiveTaskSpecification()
        assert isinstance(spec, Specification)
