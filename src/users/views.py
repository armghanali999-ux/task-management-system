"""User API views and viewsets."""

from django.contrib.auth import get_user_model
from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response

from src.shared.composition import resolve
from src.shared.utils import BusinessRuleException, EntityNotFoundException
from src.users.serializers import (
    CustomUserSerializer,
    UserListSerializer,
    UserLoginSerializer,
    UserRegistrationSerializer,
    UserUpdateSerializer,
)

CustomUser = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User CRUD operations.
    Implements REST API for user management.
    """

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    repository = resolve("user_repository")

    def get_permissions(self):
        """Override permissions for certain actions."""
        if self.action in ["register", "login"]:
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny()])
    def register(self, request):
        """Register a new user."""
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            service = resolve("user_registration_service")
            user_data = service.execute(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
                first_name=serializer.validated_data.get("first_name", ""),
                last_name=serializer.validated_data.get("last_name", ""),
            )

            # Create token for the new user
            user = CustomUser.objects.get(id=user_data["id"])
            token, created = Token.objects.get_or_create(user=user)

            return Response(
                {
                    "user": user_data,
                    "token": token.key,
                    "message": "User registered successfully",
                },
                status=status.HTTP_201_CREATED,
            )
        except BusinessRuleException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny()])
    def login(self, request):
        """Authenticate user and return token."""
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            service = resolve("user_authentication_service")
            user = service.execute(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )

            token, created = Token.objects.get_or_create(user=user)

            return Response(
                {
                    "token": token.key,
                    "user": CustomUserSerializer(user).data,
                    "message": "Login successful",
                },
                status=status.HTTP_200_OK,
            )
        except (EntityNotFoundException, BusinessRuleException) as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=["post"])
    def logout(self, request):
        """Logout user by deleting token."""
        request.user.auth_token.delete()
        return Response(
            {"message": "Logout successful"},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get current user profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["put", "patch"])
    def update_profile(self, request):
        """Update current user profile."""
        serializer = UserUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            service = resolve("user_profile_update_service")
            user = service.execute(request.user.id, **serializer.validated_data)
            return Response(
                CustomUserSerializer(user).data,
                status=status.HTTP_200_OK,
            )
        except EntityNotFoundException as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def deactivate(self, request, pk=None):
        """Deactivate a user account (admin only)."""
        try:
            self.repository.deactivate_user(pk)
            return Response(
                {"message": f"User {pk} has been deactivated"},
                status=status.HTTP_200_OK,
            )
        except EntityNotFoundException as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return UserListSerializer
        return self.serializer_class

    def list(self, request, *args, **kwargs):
        """Get user list with optional filters."""
        try:
            service = resolve("user_list_service")
            users = service.execute()
            serializer = self.get_serializer(users, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
