"""Root URL configuration."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # Authentication
    path("api/auth/token/", obtain_auth_token),
    # API endpoints
    path("api/", include("src.users.urls", namespace="users")),
    path("api/", include("src.projects.urls", namespace="projects")),
    path("api/", include("src.tasks.urls", namespace="tasks")),
    path("api/", include("src.activity.urls", namespace="activity")),
    # Web frontend
    path("", include("src.shared.urls", namespace="shared")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
