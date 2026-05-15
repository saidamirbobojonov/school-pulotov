from __future__ import annotations

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import pgettext_lazy


class NewsPostQuerySet(models.QuerySet):
    @staticmethod
    def _coerce_bool(value: object) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return bool(value)
        if isinstance(value, str):
            cleaned = value.strip().lower()
            if cleaned in {"1", "true", "t", "yes", "y", "on"}:
                return True
            if cleaned in {"0", "false", "f", "no", "n", "off", ""}:
                return False
        return bool(value)

    @classmethod
    def _rewrite_is_published_kwargs(cls, kwargs: dict) -> dict:
        if "is_published" not in kwargs and "is_published__exact" not in kwargs:
            return kwargs

        rewritten = dict(kwargs)
        value = rewritten.pop("is_published", rewritten.pop("is_published__exact", None))
        is_published = cls._coerce_bool(value)
        now = timezone.now()
        if is_published:
            rewritten["published_at__lte"] = now
        else:
            rewritten["published_at__gt"] = now
        return rewritten

    def filter(self, *args, **kwargs):
        return super().filter(*args, **self._rewrite_is_published_kwargs(kwargs))

    def exclude(self, *args, **kwargs):
        return super().exclude(*args, **self._rewrite_is_published_kwargs(kwargs))


class NewsPostManager(models.Manager.from_queryset(NewsPostQuerySet)):
    pass


class NewsPost(models.Model):
    CATEGORY_CHOICES = [
        ("events", pgettext_lazy("news category", "Events")),
        ("sport", pgettext_lazy("news category", "Sports")),
        ("academic", pgettext_lazy("news category", "Academic")),
    ]

    objects = NewsPostManager()

    title = models.CharField("Заголовок", max_length=255)
    slug = models.SlugField("Слаг", unique=True, blank=True)

    body = models.TextField("Текст", blank=True)
    cover = models.ImageField("Обложка", upload_to="news/covers/", blank=True, null=True)
    video = models.FileField("Видео", upload_to="news/videos/", blank=True, null=True)

    category = models.CharField("Категория", max_length=50, choices=CATEGORY_CHOICES, default="events")
    published_at = models.DateTimeField("Дата публикации", default=timezone.now)
    views = models.PositiveIntegerField("Просмотры", default=0)

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ["-published_at", "-id"]

    def __str__(self) -> str:
        return self.title

    def is_published(self) -> bool:
        return self.published_at <= timezone.now()

    is_published.boolean = True
    is_published.short_description = "Опубликовано"

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            base = slugify(self.title)[:180] or "news"
            slug = base
            counter = 2
            while NewsPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class NewsGallery(models.Model):
    news = models.ForeignKey(NewsPost, on_delete=models.CASCADE, verbose_name="Новость", related_name="gallery")
    image = models.ImageField("Изображение", upload_to="news/gallery/", blank=True, null=True)
    caption = models.CharField("Подпись", max_length=255, blank=True)
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Галерея новости"
        verbose_name_plural = "Галереи новостей"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Галерея для: {self.news.title}"
