from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import pgettext_lazy


class PerspectiveOverview(models.Model):
    title = models.CharField("Заголовок", max_length=255, blank=True)
    text = models.TextField("Текст", blank=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Обзор: Перспектива"
        verbose_name_plural = "Обзор: Перспектива"

    def __str__(self) -> str:
        return self.title or "Perspective Overview"

    def save(self, *args, **kwargs) -> None:
        if not self.pk and PerspectiveOverview.objects.exists():
            raise ValidationError("Можно создать только одну запись PerspectiveOverview.")
        super().save(*args, **kwargs)


class ConstructionPost(models.Model):
    title = models.CharField("Заголовок", max_length=255)
    slug = models.SlugField("Слаг", max_length=220, unique=True, blank=True)
    text = models.TextField("Текст", blank=True)
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Пост: Строительство и администрация"
        verbose_name_plural = "Посты: Строительство и администрация"
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return self.title or f"Post #{self.pk}"

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            base = slugify(self.title)[:200] or "construction"
            slug = base
            counter = 2
            while ConstructionPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class ConstructionGalleryImage(models.Model):
    post = models.ForeignKey(
        ConstructionPost,
        on_delete=models.CASCADE,
        related_name="gallery",
        verbose_name="Пост",
    )
    image = models.ImageField("Изображение", upload_to="perspective/construction/gallery/")
    caption = models.CharField("Подпись", max_length=255, blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Галерея: Строительство и администрация"
        verbose_name_plural = "Галерея: Строительство и администрация"
        ordering = ["order", "-created_at", "-id"]

    def __str__(self) -> str:
        return self.caption or f"Gallery #{self.pk}"


class PerspectiveSection(models.Model):
    class SectionType(models.TextChoices):
        ACADEMIC = "academic", pgettext_lazy("perspective section", "Academic")
        METHODICAL = "methodical", pgettext_lazy("perspective section", "Methodical")
        EDUCATIONAL = "educational", pgettext_lazy("perspective section", "Educational")

    section_type = models.CharField("Раздел", max_length=32, choices=SectionType.choices)
    title = models.CharField("Заголовок", max_length=255, blank=True)
    text = models.TextField("Текст", blank=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Раздел: Перспектива"
        verbose_name_plural = "Разделы: Перспектива"
        ordering = ["section_type", "id"]
        constraints = [
            models.UniqueConstraint(fields=["section_type"], name="uniq_perspective_section_type"),
        ]

    def __str__(self) -> str:
        return self.get_section_type_display() or "Perspective Section"
