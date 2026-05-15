from __future__ import annotations

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from people.models import SchoolClass


class SchoolEventCategory(models.Model):
    name = models.CharField("Категория", max_length=120)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Категория школьных мероприятий"
        verbose_name_plural = "Категории школьных мероприятий"
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return self.name


class SchoolEvent(models.Model):
    category = models.ForeignKey(SchoolEventCategory, on_delete=models.PROTECT, verbose_name="Категория")
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, verbose_name="Класс")

    title = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)

    start_at = models.DateTimeField("Начало")
    end_at = models.DateTimeField("Окончание", blank=True, null=True)
    place = models.CharField("Место", max_length=255)

    image = models.ImageField("Изображение (обложка)", upload_to="school_events/", blank=True, null=True)

    is_public = models.BooleanField("Показывать гостям", default=True)
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Школьное мероприятие (по классу)"
        verbose_name_plural = "Школьные мероприятия (по классам)"
        ordering = ["-start_at", "school_class__grade", "school_class__name"]
        constraints = [
            models.UniqueConstraint(fields=["school_class", "start_at", "title"], name="uniq_school_class_start_title")
        ]

    def __str__(self) -> str:
        return f"{self.title} — {self.school_class} — {self.start_at:%Y-%m-%d %H:%M}"


class SchoolEventGallery(models.Model):
    event = models.ForeignKey(
        SchoolEvent,
        on_delete=models.CASCADE,
        related_name="gallery",
        verbose_name="Мероприятие",
    )
    image = models.ImageField("Изображение", upload_to="school_events/gallery/")
    caption = models.CharField("Подпись", max_length=255, blank=True)
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Галерея школьного мероприятия"
        verbose_name_plural = "Галереи школьных мероприятий"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.event}: {self.caption or self.pk}"


class SchoolEventPost(models.Model):
    event = models.ForeignKey(
        SchoolEvent,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Мероприятие",
    )

    title = models.CharField("Заголовок", max_length=255)
    slug = models.SlugField("Слаг", max_length=220, blank=True)

    body = models.TextField("Текст", blank=True)
    cover = models.ImageField("Обложка", upload_to="school_events/posts/covers/", blank=True, null=True)
    video = models.FileField("Видео", upload_to="school_events/posts/videos/", blank=True, null=True)

    published_at = models.DateTimeField("Дата публикации", default=timezone.now)
    views = models.PositiveIntegerField("Просмотры", default=0)

    is_approved = models.BooleanField("Одобрено", default=True)
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Пост школьного мероприятия"
        verbose_name_plural = "Посты школьных мероприятий"
        ordering = ["-published_at", "-id"]
        constraints = [models.UniqueConstraint(fields=["event", "slug"], name="uniq_school_event_post_slug")]

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            base = slugify(self.title)[:180] or "post"
            slug = base
            counter = 2
            while SchoolEventPost.objects.filter(event=self.event, slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


class SchoolEventPostGallery(models.Model):
    post = models.ForeignKey(
        SchoolEventPost,
        on_delete=models.CASCADE,
        related_name="gallery",
        verbose_name="Пост",
    )
    image = models.ImageField("Изображение", upload_to="school_events/posts/gallery/")
    caption = models.CharField("Подпись", max_length=255, blank=True)
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Галерея поста школьного мероприятия"
        verbose_name_plural = "Галереи постов школьных мероприятий"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.post}: {self.caption or self.pk}"
