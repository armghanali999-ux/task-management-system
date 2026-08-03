"""User serializers for API endpoints."""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from src.users.models import UserProfile

CustomUser = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model."""

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "department",
            "job_title",
            "location",
            "preferred_language",
            "theme_preference",
            "notifications_enabled",
            "two_factor_enabled",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer for CustomUser model."""

    profile = UserProfileSerializer(read_only=True)
    display_name = serializers.CharField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "display_name",
            "phone",
            "bio",
            "avatar",
            "role",
            "is_active",
            "profile",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
        ]

    def validate(self, data):
        """Validate password confirmation."""
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        """Create new user."""
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            password=password,
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
        )
        # Create user profile
        UserProfile.objects.create(user=user)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information."""

    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "phone",
            "bio",
            "avatar",
        ]


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for listing users (limited info)."""

    display_name = serializers.CharField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "display_name",
            "avatar",
            "role",
            "is_active",
        ]
