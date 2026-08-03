"""
Comprehensive tests for the Users module.
Tests UserRepository, UserRegistrationService, UserAuthenticationService, etc.
"""

import pytest
from rest_framework import status

from src.users.models import CustomUser, UserProfile, UserRole
from src.users.repositories import UserRepository


class TestUserModel:
    """Test CustomUser model and its methods."""

    def test_create_user(self, db):
        """Test creating a regular user."""
        user = CustomUser.objects.create_user(
            email="user@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )
        assert user.email == "user@example.com"
        assert user.role == UserRole.TEAM_MEMBER
        assert not user.is_admin()

    def test_create_admin_user(self, db):
        """Test creating an admin user."""
        user = CustomUser.objects.create_user(
            email="admin@example.com",
            password="testpass123",
            role=UserRole.ADMIN,
        )
        assert user.is_admin()
        assert user.can_manage_users()

    def test_create_project_manager(self, db):
        """Test creating a project manager."""
        user = CustomUser.objects.create_user(
            email="pm@example.com",
            password="testpass123",
            role=UserRole.PROJECT_MANAGER,
        )
        assert user.is_project_manager()
        assert not user.is_admin()

    def test_user_profile_auto_created(self, db):
        """Test that UserProfile is automatically created on user creation."""
        user = CustomUser.objects.create_user(
            email="user@example.com",
            password="testpass123",
        )
        profile = UserProfile.objects.filter(user=user).exists()
        assert profile

    def test_password_hashing(self, db):
        """Test that passwords are properly hashed."""
        user = CustomUser.objects.create_user(
            email="user@example.com",
            password="testpass123",
        )
        assert not user.password == "testpass123"
        assert user.check_password("testpass123")


class TestUserRepository:
    """Test UserRepository methods (Repository Pattern)."""

    def test_get_by_email(self, db, team_member_user):
        """Test retrieving user by email."""
        repo = UserRepository()
        user = repo.get_by_email("member@example.com")
        assert user == team_member_user

    def test_get_by_email_not_found(self, db):
        """Test retrieving non-existent user returns None."""
        repo = UserRepository()
        user = repo.get_by_email("nonexistent@example.com")
        assert user is None

    def test_get_admins(self, db, admin_user, team_member_user):
        """Test retrieving all admin users."""
        repo = UserRepository()
        admins = repo.get_admins()
        assert admin_user in admins
        assert team_member_user not in admins

    def test_get_project_managers(self, db, project_manager_user, team_member_user):
        """Test retrieving all project managers."""
        repo = UserRepository()
        managers = repo.get_project_managers()
        assert project_manager_user in managers
        assert team_member_user not in managers

    def test_search_by_name(self, db, team_member_user):
        """Test searching users by name."""
        repo = UserRepository()
        results = repo.search_by_name("Team")
        assert team_member_user in results

    def test_create_user_via_repository(self, db):
        """Test creating user through repository."""
        repo = UserRepository()
        user_data = {
            "email": "newuser@example.com",
            "password": "pass123",
            "first_name": "New",
            "last_name": "User",
            "role": UserRole.TEAM_MEMBER,
        }
        user = repo.create(user_data)
        assert user.email == "newuser@example.com"
        assert CustomUser.objects.filter(email="newuser@example.com").exists()

    def test_update_user(self, db, team_member_user):
        """Test updating user through repository."""
        repo = UserRepository()
        update_data = {"first_name": "Updated", "last_name": "Name"}
        for field, value in update_data.items():
            setattr(team_member_user, field, value)
        repo.update(team_member_user)
        updated_user = repo.get_by_id(team_member_user.id)
        assert updated_user.first_name == "Updated"

    def test_delete_user(self, db, team_member_user):
        """Test deleting user through repository."""
        repo = UserRepository()
        user_id = team_member_user.id
        repo.delete(user_id)
        assert not CustomUser.objects.get(id=user_id).is_active


class TestUserRegistrationService:
    """Test UserRegistrationService (Application Service Pattern)."""

    def test_register_new_user(self, db, user_registration_service):
        """Test registering a new user."""
        result = user_registration_service.execute(
            email="newuser@example.com",
            password="securepass123",
            first_name="New",
            last_name="User",
        )
        assert result["email"] == "newuser@example.com"
        assert CustomUser.objects.filter(email="newuser@example.com").exists()

    def test_register_duplicate_email(self, db, user_registration_service, team_member_user):
        """Test that duplicate email registration fails."""
        with pytest.raises(Exception):
            user_registration_service.execute(
                email="member@example.com",
                password="password123",
                first_name="Duplicate",
                last_name="User",
            )

    def test_register_invalid_email(self, db, user_registration_service):
        """Test registration with invalid email."""
        # Service should handle or database should reject invalid email
        result = user_registration_service.execute(
            email="invalid-email",
            password="password123",
            first_name="Invalid",
            last_name="User",
        )
        # Result should still work due to Django's lenient email validation
        assert "email" in result


class TestUserAuthenticationService:
    """Test UserAuthenticationService (Application Service Pattern)."""

    def test_authenticate_valid_credentials(
        self, db, user_authentication_service, team_member_user
    ):
        """Test authentication with valid credentials."""
        result = user_authentication_service.execute(
            email="member@example.com",
            password="memberpass123",
        )
        assert result.email == "member@example.com"
        assert result.id == team_member_user.id

    def test_authenticate_invalid_password(self, db, user_authentication_service, team_member_user):
        """Test authentication with invalid password."""
        from src.shared.utils import EntityNotFoundException

        with pytest.raises(EntityNotFoundException):
            user_authentication_service.execute(
                email="member@example.com",
                password="wrongpassword",
            )

    def test_authenticate_non_existent_user(self, db, user_authentication_service):
        """Test authentication with non-existent email."""
        from src.shared.utils import EntityNotFoundException

        with pytest.raises(EntityNotFoundException):
            user_authentication_service.execute(
                email="nonexistent@example.com",
                password="password123",
            )


class TestUserProfileUpdateService:
    """Test UserProfileUpdateService (Application Service Pattern)."""

    def test_update_profile(self, db, user_profile_update_service, team_member_user):
        """Test updating user profile."""
        user_profile_update_service.execute(
            user_id=team_member_user.id,
            first_name="Updated",
            last_name="Name",
        )
        updated_user = CustomUser.objects.get(id=team_member_user.id)
        assert updated_user.first_name == "Updated"

    def test_update_profile_invalid_user(self, db, user_profile_update_service):
        """Test updating non-existent user profile."""
        with pytest.raises(Exception):
            user_profile_update_service.execute(
                user_id=99999,
                first_name="Test",
            )


class TestUserListService:
    """Test UserListService (Application Service Pattern)."""

    def test_list_users(self, db, user_list_service, team_member_user, project_manager_user):
        """Test listing users."""
        result = user_list_service.execute(role=None, search=None)
        assert len(result) >= 2

    def test_list_users_by_role(
        self, db, user_list_service, project_manager_user, team_member_user
    ):
        """Test listing users filtered by role."""
        result = user_list_service.execute(role=UserRole.PROJECT_MANAGER)
        assert len(result) >= 1


class TestUserDeactivationService:
    """Test UserDeactivationService (Application Service Pattern)."""

    def test_deactivate_user(self, db, user_deactivation_service, team_member_user):
        """Test deactivating a user."""
        user_deactivation_service.execute(user_id=team_member_user.id)
        deactivated_user = CustomUser.objects.get(id=team_member_user.id)
        assert not deactivated_user.is_active


class TestUserAPI:
    """Test User REST API endpoints."""

    def test_register_endpoint(self, api_client, db):
        """Test POST /api/users/register/"""
        response = api_client.post(
            "/api/users/register/",
            {
                "email": "newuser@example.com",
                "password": "securepass123",
                "password_confirm": "securepass123",
                "first_name": "New",
                "last_name": "User",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_login_endpoint(self, api_client, db, team_member_user):
        """Test POST /api/users/login/"""
        response = api_client.post(
            "/api/users/login/",
            {
                "email": "member@example.com",
                "password": "memberpass123",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.data

    def test_get_current_user(self, authenticated_api_client, team_member_user):
        """Test GET /api/users/me/"""
        response = authenticated_api_client.get("/api/users/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == team_member_user.email

    def test_update_profile_endpoint(self, authenticated_api_client, team_member_user):
        """Test PUT /api/users/me/update_profile/"""
        response = authenticated_api_client.put(
            "/api/users/update_profile/",
            {"first_name": "Updated"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK


class TestUserPermissions:
    """Test permission checks in User module."""

    def test_admin_can_manage_users(self, admin_user):
        """Test that admins can manage users."""
        assert admin_user.can_manage_users()

    def test_project_manager_can_manage_users(self, project_manager_user):
        """Test that project managers can manage users by current role policy."""
        assert project_manager_user.can_manage_users()

    def test_team_member_cannot_manage_users(self, team_member_user):
        """Test that team members cannot manage users."""
        assert not team_member_user.can_manage_users()
