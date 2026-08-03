"""Activity app URLs."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from src.activity.views import ActivityLogViewSet

router = DefaultRouter()
router.register(r"activity", ActivityLogViewSet, basename="activity")

app_name = "activity"

urlpatterns = [
    path("", include(router.urls)),
]
