from __future__ import annotations

import json
from urllib.parse import urlparse

from django.conf import settings
from django.db import models
from django.urls import NoReverseMatch, reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class MenuItem(models.Model):
    class MenuType(models.TextChoices):
        PUBLIC = "public", _("Public")
        STUDENT = "student", _("Student")
        TEACHER = "teacher", _("Teacher")

    title = models.CharField("Название", max_length=255)
    menu_type = models.CharField(
        "Тип меню",
        max_length=16,
        choices=MenuType.choices,
        default=MenuType.PUBLIC,
    )
    order = models.PositiveIntegerField("Порядок", default=0)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="children",
        verbose_name="Родитель",
    )
    is_active = models.BooleanField("Активен", default=True)
    show_in_footer = models.BooleanField("Показывать в футере", default=False)

    route_name = models.CharField("Имя маршрута", max_length=255, blank=True)
    url_kwargs_json = models.TextField("Параметры URL (JSON)", blank=True)
    custom_url = models.CharField("Пользовательский URL", max_length=255, blank=True)

    class Meta:
        verbose_name = "Пункт меню"
        verbose_name_plural = "Пункты меню"
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.title

    def get_url(self) -> str:
        if self.custom_url:
            return self.custom_url
        if self.route_name:
            kwargs: dict = {}
            if self.url_kwargs_json:
                try:
                    data = json.loads(self.url_kwargs_json)
                    if isinstance(data, dict):
                        kwargs = data
                except json.JSONDecodeError:
                    kwargs = {}
            try:
                return reverse(self.route_name, kwargs=kwargs)
            except NoReverseMatch:
                return "#"
        return "#"

    @property
    def slug(self) -> str:
        url = self.get_url()
        path = urlparse(url).path
        parts = [part for part in path.split("/") if part]
        language_codes = {code for code, _ in settings.LANGUAGES}
        if parts and parts[0] in language_codes:
            parts = parts[1:]
        if not parts:
            return ""
        return slugify("-".join(parts))

    @classmethod
    def match_for_request(cls, request, *, menu_types: set[str] | None = None):
        url_name = getattr(getattr(request, "resolver_match", None), "url_name", None)
        if url_name:
            qs = cls.objects.filter(is_active=True, route_name=url_name)
            if menu_types:
                qs = qs.filter(menu_type__in=menu_types)
            item = qs.order_by("order", "id").first()
            if item:
                return item

        current_path = request.path.rstrip("/") or "/"
        qs = cls.objects.filter(is_active=True)
        if menu_types:
            qs = qs.filter(menu_type__in=menu_types)
        best_item = None
        best_len = -1
        for item in qs.order_by("order", "id"):
            item_url = (item.get_url() or "").rstrip("/") or "/"
            if item_url == current_path:
                return item
            if item_url != "/" and (current_path.startswith(item_url + "/") or current_path == item_url):
                if len(item_url) > best_len:
                    best_item = item
                    best_len = len(item_url)

        return best_item
