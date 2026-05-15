from __future__ import annotations

from typing import Any

from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import render
from django.views.generic import DetailView, ListView

from core.pagination import page_has_other_pages
from events_extracurricular.models import ExtracurricularPost

from .models import SchoolEvent, SchoolEventPost

ACTIVITY_KEY_ALIASES = {
    "academic-activity": "academic",
    "education": "educational",
    "educatinal": "educational",
    "educational-activity": "educational",
    "methodological": "methodical",
    "methodical-activity": "methodical",
    "metodical": "methodical",
}

ACTIVITY_PAGE_CONTENT: dict[str, dict[str, Any]] = {}

BLOCKED_ACTIVITY_KEYS = {"academic", "educational", "methodical"}


def _normalize_activity_key(type_key: str) -> str:
    normalized = (type_key or "").strip().lower()
    if not normalized:
        return ""
    normalized = ACTIVITY_KEY_ALIASES.get(normalized, normalized)
    if normalized.endswith("-activity"):
        normalized = normalized[: -len("-activity")]
    return ACTIVITY_KEY_ALIASES.get(normalized, normalized)


def _posts_queryset_for_activity(activity_key: str):
    activity = ACTIVITY_PAGE_CONTENT.get(activity_key) or {}
    source = activity.get("source") or "school"

    if source == "extracurricular":
        return (
            ExtracurricularPost.objects.select_related(
                "event",
                "event__category",
                "event__school_class",
            )
            .prefetch_related("gallery")
            .filter(event__is_public=True, is_approved=True)
            .order_by("-published_at", "-id")
        )

    return (
        SchoolEventPost.objects.select_related(
            "event",
            "event__category",
            "event__school_class",
        )
        .prefetch_related("gallery")
        .filter(event__is_public=True, is_approved=True)
        .order_by("-published_at", "-id")
    )


def _append_gallery_item(
    gallery_items: list[dict[str, str]],
    seen_urls: set[str],
    image_field,
    *,
    caption: str = "",
    alt: str = "",
):
    if not image_field:
        return

    try:
        image_url = image_field.url
    except Exception:
        return

    if not image_url or image_url in seen_urls:
        return

    seen_urls.add(image_url)
    gallery_items.append(
        {
            "url": image_url,
            "caption": (caption or "").strip(),
            "alt": (alt or "").strip() or "Activity image",
        }
    )


def school_event_type_posts(request, type_key: str):
    normalized_type_key = _normalize_activity_key(type_key)
    if normalized_type_key in BLOCKED_ACTIVITY_KEYS:
        raise Http404
    posts_qs = _posts_queryset_for_activity(normalized_type_key)
    posts = list(posts_qs[:24])
    hero_posts = posts[:3]

    activity = ACTIVITY_PAGE_CONTENT.get(
        normalized_type_key,
        {
            "name": normalized_type_key.replace("-", " ").title() or "Activity",
            "description": "Latest posts and photos from this activity.",
            "overview_title": "Activity overview",
            "overview_text": "This page shows recent posts and a gallery for the selected activity type.",
            "detail_url_name": "school-event-detail",
        },
    )

    gallery_items: list[dict[str, str]] = []
    seen_urls: set[str] = set()
    max_gallery_items = 15
    gallery_album = (activity.get("gallery_album") or "").strip()
    activity_nav_buttons: list[dict[str, Any]] = []
    activity_nav_parent_title = ""

    if gallery_album:
        try:
            from site_content.models import GalleryImage

            category_images = (
                GalleryImage.objects.filter(is_public=True, album__is_public=True, album__slug=gallery_album)
                .order_by("order", "-created_at", "-id")[:max_gallery_items]
            )
            for image in category_images:
                _append_gallery_item(
                    gallery_items,
                    seen_urls,
                    image.image,
                    caption=image.caption,
                    alt=image.caption or activity.get("name") or "Activity image",
                )
        except Exception:
            pass

    if not gallery_album:
        for post in posts:
            if len(gallery_items) >= max_gallery_items:
                break

            for image in post.gallery.all():
                _append_gallery_item(
                    gallery_items,
                    seen_urls,
                    image.image,
                    caption=image.caption or post.title,
                    alt=post.title,
                )
                if len(gallery_items) >= max_gallery_items:
                    break

            if len(gallery_items) >= max_gallery_items:
                break
            _append_gallery_item(
                gallery_items,
                seen_urls,
                post.cover,
                caption=post.title,
                alt=post.title,
            )

            if len(gallery_items) >= max_gallery_items:
                break
            _append_gallery_item(
                gallery_items,
                seen_urls,
                post.event.image,
                caption=post.event.title,
                alt=post.event.title,
            )

    try:
        from navigation.models import MenuItem

        active_menu_item = MenuItem.match_for_request(request, menu_types={MenuItem.MenuType.PUBLIC})
        if active_menu_item:
            main_item = active_menu_item.parent or active_menu_item
            activity_nav_parent_title = (main_item.title or "").strip()
            child_items = list(
                main_item.children.filter(
                    is_active=True,
                    menu_type=MenuItem.MenuType.PUBLIC,
                ).order_by("order", "id")
            )
            activity_nav_buttons = [
                {
                    "title": item.title,
                    "url": item.get_url(),
                    "is_active": item.id == active_menu_item.id,
                }
                for item in child_items
            ]
    except Exception:
        pass

    return render(
        request,
        "school-event-posts.html",
        {
            "activity": activity,
            "activity_key": normalized_type_key,
            "detail_url_name": activity.get("detail_url_name") or "school-event-detail",
            "hero_posts": hero_posts,
            "posts_count": len(posts),
            "gallery_items": gallery_items,
            "activity_nav_parent_title": activity_nav_parent_title,
            "activity_nav_buttons": activity_nav_buttons,
            "posts": posts,
        },
    )


class SchoolEventListView(ListView):
    template_name = "school-events.html"
    context_object_name = "events"
    paginate_by = 9

    featured_event: SchoolEvent | None = None

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
            SchoolEvent.objects.select_related("category", "school_class")
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
            SchoolEvent.objects.filter(is_public=True)
            .values("category_id", "category__name")
            .annotate(count=Count("id"))
            .order_by("category__order", "category__name")
        )
        years = [d.year for d in SchoolEvent.objects.filter(is_public=True).dates("start_at", "year", order="DESC")]

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


class SchoolEventDetailView(DetailView):
    template_name = "event-detail.html"
    context_object_name = "event"

    def get_queryset(self):
        return (
            SchoolEvent.objects.select_related("category", "school_class")
            .filter(is_public=True)
            .prefetch_related("gallery")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event: SchoolEvent = context["event"]

        context["event_kind"] = "School Event"
        context["back_url_name"] = "school-events"
        context["gallery_images"] = list(event.gallery.all())
        context["related_events"] = list(
            SchoolEvent.objects.select_related("category", "school_class")
            .filter(is_public=True)
            .exclude(pk=event.pk)
            .order_by("-start_at", "-id")[:3]
        )

        return context
