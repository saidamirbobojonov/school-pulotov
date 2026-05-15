from __future__ import annotations

from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q
from django.views.generic import DetailView, ListView

from core.pagination import page_has_other_pages

from .models import Club


def _translated_field_names(model, base_field: str) -> list[str]:
    field_names: list[str] = []
    try:
        model._meta.get_field(base_field)
        field_names.append(base_field)
    except FieldDoesNotExist:
        pass

    languages = getattr(settings, "MODELTRANSLATION_LANGUAGES", None) or [code for code, _ in settings.LANGUAGES]
    for code in languages:
        name = f"{base_field}_{code}"
        try:
            model._meta.get_field(name)
            field_names.append(name)
        except FieldDoesNotExist:
            continue

    return field_names


class ClubListView(ListView):
    template_name = "clubs.html"
    context_object_name = "clubs"
    paginate_by = 9

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
        queryset = Club.objects.select_related("leader").filter(is_public=True).order_by("name")

        query = ((self.request.GET.get("q") or "").strip())[:100]
        if query:
            club_q = Q()
            for field in _translated_field_names(Club, "name"):
                club_q |= Q(**{f"{field}__icontains": query})
            for field in _translated_field_names(Club, "description"):
                club_q |= Q(**{f"{field}__icontains": query})
            for field in _translated_field_names(Club, "schedule_text"):
                club_q |= Q(**{f"{field}__icontains": query})

            try:
                from people.models import Staff

                for field in _translated_field_names(Staff, "full_name"):
                    club_q |= Q(**{f"leader__{field}__icontains": query})
            except Exception:
                pass

            queryset = queryset.filter(club_q)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        params = self.request.GET.copy()
        params.pop("page", None)
        qs = params.urlencode()

        context["search_query"] = ((self.request.GET.get("q") or "").strip())[:100]
        context["querystring"] = f"&{qs}" if qs else ""

        return context


class ClubDetailView(DetailView):
    template_name = "club-detail.html"
    context_object_name = "club"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Club.objects.select_related("leader").prefetch_related("gallery").filter(is_public=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        club: Club = context["club"]

        context["gallery_images"] = list(club.gallery.all())
        context["more_clubs"] = list(Club.objects.filter(is_public=True).exclude(pk=club.pk).order_by("name")[:3])

        return context
