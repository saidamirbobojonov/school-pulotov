from __future__ import annotations

from django.db import OperationalError, ProgrammingError
from django.views.generic import DetailView, TemplateView

from .models import ConstructionPost, PerspectiveOverview, PerspectiveSection


class PerspectivePageView(TemplateView):
    template_name = "perspective.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["overview"] = None
        context["construction_posts"] = []
        context["sections"] = {
            "academic": None,
            "methodical": None,
            "educational": None,
        }

        try:
            context["overview"] = PerspectiveOverview.objects.first()
            context["construction_posts"] = list(
                ConstructionPost.objects.prefetch_related("gallery").all().order_by("-created_at", "-id")
            )
            for section in PerspectiveSection.objects.all():
                context["sections"][section.section_type] = section
        except (OperationalError, ProgrammingError):
            pass

        return context


class ConstructionPostDetailView(DetailView):
    model = ConstructionPost
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "perspective-detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["gallery_images"] = []
        try:
            context["gallery_images"] = list(self.object.gallery.all().order_by("order", "-created_at", "-id"))
        except Exception:
            pass
        return context
