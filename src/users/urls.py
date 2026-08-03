"""User app URLs."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from src.users.views import UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

app_name = "users"

urlpatterns = [
    path("", include(router.urls)),
]
