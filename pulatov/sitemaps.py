from __future__ import annotations

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone

from clubs.models import Club
from events_extracurricular.models import ExtracurricularEvent
from events_school.models import SchoolEvent
from news.models import NewsPost
from perspective.models import ConstructionPost


class StaticViewSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.7

    def items(self) -> list[str]:
        return [
            "index",
            "about",
            "achievments",
            "admissions",
            "clubs",
            "contact",
            "employees",
            "gallery",
            "methodical-materials",
            "perspective",
            "news",
            "schedules",
            "students-community",
            "teachers-committee-public",   # ✅ ВАЖНО: исправили имя
            "school-events",
            "extracurricular-events",
        ]

    def location(self, item: str) -> str:
        return reverse(item)


class NewsSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return NewsPost.objects.filter(published_at__lte=timezone.now())

    def lastmod(self, obj: NewsPost):
        return obj.published_at

    def location(self, obj: NewsPost) -> str:
        return reverse("news-detail", kwargs={"slug": obj.slug})


class ClubSitemap(Sitemap):
    protocol = "https"
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Club.objects.filter(is_public=True)

    def lastmod(self, obj: Club):
        return obj.created_at

    def location(self, obj: Club) -> str:
        return reverse("club-detail", kwargs={"slug": obj.slug})


class SchoolEventSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return SchoolEvent.objects.filter(is_public=True)

    def lastmod(self, obj: SchoolEvent):
        return obj.start_at

    def location(self, obj: SchoolEvent) -> str:
        return reverse("school-event-detail", kwargs={"pk": obj.pk})


class ExtracurricularEventSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return ExtracurricularEvent.objects.filter(is_public=True)

    def lastmod(self, obj: ExtracurricularEvent):
        return obj.start_at

    def location(self, obj: ExtracurricularEvent) -> str:
        return reverse("extracurricular-event-detail", kwargs={"pk": obj.pk})


class ConstructionPostSitemap(Sitemap):
    protocol = "https"
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return ConstructionPost.objects.all().order_by("-created_at", "-id")

    def lastmod(self, obj: ConstructionPost):
        return obj.created_at

    def location(self, obj: ConstructionPost) -> str:
        return reverse("perspective-construction", kwargs={"slug": obj.slug})


SITEMAPS = {
    "static": StaticViewSitemap,
    "news": NewsSitemap,
    "clubs": ClubSitemap,
    "school-events": SchoolEventSitemap,
    "extracurricular-events": ExtracurricularEventSitemap,
    "construction-posts": ConstructionPostSitemap,
}
