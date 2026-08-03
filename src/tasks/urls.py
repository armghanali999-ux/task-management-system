"""Task app URLs."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from src.tasks.views import TaskViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")

app_name = "tasks"

urlpatterns = [
    path("", include(router.urls)),
]
