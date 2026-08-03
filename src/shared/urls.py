"""Shared URLs for frontend and dashboard."""

from django.urls import path

from src.shared.dashboard_views import admin_dashboard, dashboard
from src.shared.views import FrontendPageView, IndexView

app_name = "shared"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path(
        "login/",
        FrontendPageView.as_view(template_name="auth/login.html", page_name="login"),
        name="login",
    ),
    path(
        "register/",
        FrontendPageView.as_view(template_name="auth/register.html", page_name="register"),
        name="register",
    ),
    path(
        "dashboard/",
        FrontendPageView.as_view(template_name="dashboard.html", page_name="dashboard"),
        name="dashboard-page",
    ),
    path(
        "projects/",
        FrontendPageView.as_view(template_name="projects/list.html", page_name="projects"),
        name="project-list",
    ),
    path(
        "projects/<int:pk>/",
        FrontendPageView.as_view(template_name="projects/detail.html", page_name="project-detail"),
        name="project-detail",
    ),
    path(
        "tasks/",
        FrontendPageView.as_view(template_name="tasks/list.html", page_name="tasks"),
        name="task-list",
    ),
    path(
        "tasks/<int:pk>/",
        FrontendPageView.as_view(template_name="tasks/detail.html", page_name="task-detail"),
        name="task-detail",
    ),
    path(
        "activity/",
        FrontendPageView.as_view(template_name="activity.html", page_name="activity"),
        name="activity-page",
    ),
    path(
        "profile/",
        FrontendPageView.as_view(template_name="profile.html", page_name="profile"),
        name="profile",
    ),
    path("api/dashboard/", dashboard, name="dashboard"),
    path("api/admin-dashboard/", admin_dashboard, name="admin_dashboard"),
]
