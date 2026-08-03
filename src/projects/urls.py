"""Project app URLs."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from src.projects.views import ProjectViewSet

router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="project")

app_name = "projects"

urlpatterns = [
    path("", include(router.urls)),
]
