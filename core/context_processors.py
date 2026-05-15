from __future__ import annotations

from typing import Any


def site_context(request) -> dict[str, Any]:
    try:
        from django.db.utils import OperationalError, ProgrammingError
        from django.utils import timezone
        from django.db import models
        from django.db.models import Prefetch

        from news.models import NewsPost
        from contacts.models import ContactPage
        from navigation.models import MenuItem
        from site_content.models import (
            Announcement,
            FAQItem,
            GalleryImage,
            Hero,
            SchoolContent,
            SchoolName,
            SocialNetwork,
        )
    except Exception:
        return {}

    context: dict[str, Any] = {
        "contact_page": None,
        "school_info": None,
        "school_content": None,
        "social_networks": [],
        "announcements_active": [],
        "announcements_all": [],
        "heroes": [],
        "latest_news": [],
        "home_gallery_images": [],
        "faq_items": [],
        "menu_items": [],
        "active_menu_item": None,
        "portal_menu_items": [],
        "footer_menu_items": [],
    }

    try:
        context["contact_page"] = ContactPage.objects.first()
    except (OperationalError, ProgrammingError):
        pass

    try:
        context["school_info"] = SchoolName.objects.first()
    except (OperationalError, ProgrammingError):
        pass

    try:
        context["school_content"] = SchoolContent.objects.first()
    except (OperationalError, ProgrammingError):
        pass

    try:
        context["social_networks"] = list(SocialNetwork.objects.all().order_by("order", "created_at"))
    except (OperationalError, ProgrammingError):
        pass

    try:
        now = timezone.now()
        context["announcements_active"] = list(
            Announcement.objects.filter(start_at__lte=now)
            .filter(models.Q(end_at__isnull=True) | models.Q(end_at__gte=now))
            .order_by("-start_at", "-id")[:5]
        )
        context["announcements_all"] = list(Announcement.objects.all().order_by("-start_at", "-id")[:100])
    except (OperationalError, ProgrammingError):
        pass

    try:
        context["latest_news"] = list(NewsPost.objects.all().order_by("-published_at", "-id")[:6])
    except (OperationalError, ProgrammingError):
        pass

    try:
        context["home_gallery_images"] = list(
            GalleryImage.objects.filter(is_public=True, album__is_public=True).order_by("order", "-created_at")[:12]
        )
    except (OperationalError, ProgrammingError):
        pass

    try:
        context["faq_items"] = list(FAQItem.objects.filter(is_active=True).order_by("order", "id")[:20])
    except (OperationalError, ProgrammingError):
        pass

    try:
        children_qs = MenuItem.objects.filter(is_active=True).order_by("order", "id")

        if request.path.startswith("/portal/"):
            role = getattr(getattr(request, "user", None), "role", None)
            is_staff = bool(getattr(getattr(request, "user", None), "is_staff", False))
            is_superuser = bool(getattr(getattr(request, "user", None), "is_superuser", False))

            if is_superuser or is_staff or role == "teacher":
                menu_types = {"student", "teacher", "secure"}
            else:
                menu_types = {"student", "secure"}
        else:
            menu_types = {"public"}

        children_qs = children_qs.filter(menu_type__in=menu_types)
        context["menu_items"] = list(
            MenuItem.objects.filter(is_active=True, parent__isnull=True)
            .prefetch_related(Prefetch("children", queryset=children_qs))
            .filter(menu_type__in=menu_types)
            .order_by("order", "id")
        )
        context["active_menu_item"] = MenuItem.match_for_request(request, menu_types=menu_types)
    except (OperationalError, ProgrammingError):
        pass

    try:
        context["footer_menu_items"] = list(
            MenuItem.objects.filter(is_active=True, show_in_footer=True, menu_type=MenuItem.MenuType.PUBLIC)
            .order_by("order", "id")
        )
    except (OperationalError, ProgrammingError):
        pass

    try:
        user = getattr(request, "user", None)
        if user and getattr(user, "is_authenticated", False):
            role = getattr(user, "role", None)
            is_staff = bool(getattr(user, "is_staff", False))
            is_superuser = bool(getattr(user, "is_superuser", False))

            if is_superuser or is_staff or role == "teacher":
                portal_menu_types = {"student", "teacher", "secure"}
            else:
                portal_menu_types = {"student", "secure"}

            portal_children_qs = (
                MenuItem.objects.filter(is_active=True, menu_type__in=portal_menu_types)
                .order_by("order", "id")
            )
            context["portal_menu_items"] = list(
                MenuItem.objects.filter(is_active=True, parent__isnull=True, menu_type__in=portal_menu_types)
                .prefetch_related(Prefetch("children", queryset=portal_children_qs))
                .order_by("order", "id")
            )
    except (OperationalError, ProgrammingError):
        pass

    try:
        active_menu_item = context.get("active_menu_item")
        heroes_qs = Hero.objects.all()
        if active_menu_item:
            heroes_qs = heroes_qs.filter(models.Q(menu_item__isnull=True) | models.Q(menu_item=active_menu_item))
        else:
            heroes_qs = heroes_qs.filter(menu_item__isnull=True)
        context["heroes"] = list(heroes_qs.order_by("order", "id"))
    except (OperationalError, ProgrammingError):
        pass

    return context
