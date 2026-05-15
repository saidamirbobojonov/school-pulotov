from __future__ import annotations

from django.db.utils import OperationalError, ProgrammingError
from django.db.models import Count, Q
from django.views.generic import ListView

from core.pagination import page_has_other_pages

from .models import CompetitionResult, CompetitionType, SchoolHonor


class AchievementsListView(ListView):
    template_name = "achievments.html"
    context_object_name = "results"
    paginate_by = 12

    def paginate_queryset(self, queryset, page_size):
        paginator = self.get_paginator(
            queryset,
            page_size,
            orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty(),
        )
        page_kwarg = self.page_kwarg
        page_number = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        page_obj = paginator.get_page(page_number)

        return paginator, page_obj, page_obj.object_list, page_has_other_pages(page_obj)

    def get_queryset(self):
        queryset = (
            CompetitionResult.objects.select_related(
                "competition_type",
                "student",
                "student__school_class",
                "subject",
            )
            .all()
            .order_by("-year", "-created_at", "-id")
        )

        query = ((self.request.GET.get("q") or "").strip())[:100]
        if query:
            queryset = queryset.filter(Q(student__full_name__icontains=query) | Q(title__icontains=query))

        year = (self.request.GET.get("year") or "").strip()
        if year.isdigit():
            queryset = queryset.filter(year=int(year))

        level = (self.request.GET.get("level") or "").strip()
        if level:
            queryset = queryset.filter(level=level)

        competition_type = (self.request.GET.get("type") or "").strip()
        if competition_type.isdigit():
            queryset = queryset.filter(competition_type_id=int(competition_type))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        years = list(
            CompetitionResult.objects.values_list("year", flat=True).distinct().order_by("-year")[:20]
        )

        levels = [{"level": code, "label": label} for code, label in CompetitionResult.LEVEL_CHOICES]

        type_counts = list(
            CompetitionType.objects.annotate(count=Count("competitionresult"))
            .filter(count__gt=0)
            .order_by("order", "name")
            .values("id", "name", "count")
        )

        try:
            school_honors = list(SchoolHonor.objects.filter(is_public=True).order_by("order", "-year", "-id")[:10])
        except (OperationalError, ProgrammingError):
            school_honors = []

        params = self.request.GET.copy()
        params.pop("page", None)
        qs = params.urlencode()

        context["years"] = years
        context["levels"] = levels
        context["type_counts"] = type_counts
        context["school_honors"] = school_honors

        context["search_query"] = ((self.request.GET.get("q") or "").strip())[:100]
        context["active_year"] = (self.request.GET.get("year") or "").strip()
        context["active_level"] = (self.request.GET.get("level") or "").strip()
        context["active_type"] = (self.request.GET.get("type") or "").strip()
        context["querystring"] = f"&{qs}" if qs else ""

        return context
