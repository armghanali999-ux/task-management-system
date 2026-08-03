"""Shared views for frontend."""

from django.views.generic import TemplateView


class IndexView(TemplateView):
    """Landing page view."""

    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class FrontendPageView(TemplateView):
    """Render a project-level frontend page backed by the REST API."""

    page_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_name"] = self.page_name
        return context
