from __future__ import annotations

from django.db.models import Count, Q
from django.views.generic import DetailView, ListView

from core.pagination import page_has_other_pages

from .models import ExtracurricularEvent


class ExtracurricularEventListView(ListView):
    template_name = "extracurricular-events.html"
    context_object_name = "events"
    paginate_by = 9

    featured_event: ExtracurricularEvent | None = None

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
            ExtracurricularEvent.objects.select_related("category", "school_class")
            .filter(is_public=True)
            .order_by("-start_at", "-id")
        )

        active_category = (self.request.GET.get("category") or "").strip()
        if active_category.isdigit():
            queryset = queryset.filter(category_id=int(active_category))

        active_year = (self.request.GET.get("year") or "").strip()
        if active_year.isdigit():
            queryset = queryset.filter(start_at__year=int(active_year))

        query = ((self.request.GET.get("q") or "").strip())[:100]
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(place__icontains=query))

        page = (self.request.GET.get("page") or "1").strip()
        if page == "1":
            self.featured_event = queryset.first()
            if self.featured_event:
                queryset = queryset.exclude(pk=self.featured_event.pk)
        else:
            self.featured_event = None

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        categories = list(
            ExtracurricularEvent.objects.filter(is_public=True)
            .values("category_id", "category__name")
            .annotate(count=Count("id"))
            .order_by("category__order", "category__name")
        )
        years = [
            d.year
            for d in ExtracurricularEvent.objects.filter(is_public=True).dates("start_at", "year", order="DESC")
        ]

        params = self.request.GET.copy()
        params.pop("page", None)
        qs = params.urlencode()

        context["featured_event"] = self.featured_event
        context["categories"] = categories
        context["years"] = years
        context["active_category"] = (self.request.GET.get("category") or "").strip()
        context["active_year"] = (self.request.GET.get("year") or "").strip()
        context["search_query"] = ((self.request.GET.get("q") or "").strip())[:100]
        context["querystring"] = f"&{qs}" if qs else ""

        return context


class ExtracurricularEventDetailView(DetailView):
    template_name = "event-detail.html"
    context_object_name = "event"

    def get_queryset(self):
        return (
            ExtracurricularEvent.objects.select_related("category", "school_class")
            .filter(is_public=True)
            .prefetch_related("gallery")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event: ExtracurricularEvent = context["event"]

        context["event_kind"] = "Extracurricular Event"
        context["back_url_name"] = "extracurricular-events"
        context["gallery_images"] = list(event.gallery.all())
        context["related_events"] = list(
            ExtracurricularEvent.objects.select_related("category", "school_class")
            .filter(is_public=True)
            .exclude(pk=event.pk)
            .order_by("-start_at", "-id")[:3]
        )

        return context
