from __future__ import annotations

from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from people.models import SchoolClass

GRADE_CHOICES = [(grade, str(grade)) for grade in range(1, 12)]


class ExtracurricularCategory(models.Model):
    name = models.CharField("Категория", max_length=120, unique=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Категория внешкольных занятий"
        verbose_name_plural = "Категории внешкольных занятий"
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return self.name


class ExtracurricularEvent(models.Model):
    category = models.ForeignKey(ExtracurricularCategory, on_delete=models.PROTECT, verbose_name="Категория")
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, verbose_name="Класс")

    title = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)

    start_at = models.DateTimeField("Начало")
    end_at = models.DateTimeField("Окончание", blank=True, null=True)
    place = models.CharField("Место", max_length=255)

    image = models.ImageField("Изображение (обложка события)", upload_to="extracurricular/", blank=True, null=True)

    is_public = models.BooleanField("Показывать гостям", default=True)
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Внешкольное событие (по классу)"
        verbose_name_plural = "Внешкольные события (по классам)"
        ordering = ["-start_at", "school_class__grade", "school_class__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["school_class", "start_at", "title"],
                name="uniq_extr_class_start_title",
            )
        ]

    def __str__(self) -> str:
        return f"{self.title} — {self.school_class} — {self.start_at:%Y-%m-%d %H:%M}"


class ExtracurricularEventGallery(models.Model):
    event = models.ForeignKey(
        ExtracurricularEvent,
        on_delete=models.CASCADE,
        related_name="gallery",
        verbose_name="Событие",
    )
    image = models.ImageField("Изображение", upload_to="extracurricular/gallery/")
    caption = models.CharField("Подпись", max_length=255, blank=True)
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Галерея внешкольного события"
        verbose_name_plural = "Галереи внешкольных событий"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.event}: {self.caption or self.pk}"


class ExtracurricularPost(models.Model):
    event = models.ForeignKey(
        ExtracurricularEvent,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Событие",
    )

    title = models.CharField("Заголовок", max_length=255)
    slug = models.SlugField("Слаг", max_length=220, blank=True)

    body = models.TextField("Текст", blank=True)
    cover = models.ImageField("Обложка", upload_to="extracurricular/posts/covers/", blank=True, null=True)
    video = models.FileField("Видео", upload_to="extracurricular/posts/videos/", blank=True, null=True)

    published_at = models.DateTimeField("Дата публикации", default=timezone.now)
    views = models.PositiveIntegerField("Просмотры", default=0)

    is_approved = models.BooleanField("Одобрено", default=True)
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Пост внешкольного события"
        verbose_name_plural = "Посты внешкольных событий"
        ordering = ["-published_at", "-id"]
        constraints = [models.UniqueConstraint(fields=["event", "slug"], name="uniq_extr_event_post_slug")]

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            base = slugify(self.title)[:180] or "post"
            slug = base
            counter = 2
            while ExtracurricularPost.objects.filter(event=self.event, slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


class ExtracurricularPostGallery(models.Model):
    post = models.ForeignKey(
        ExtracurricularPost,
        on_delete=models.CASCADE,
        related_name="gallery",
        verbose_name="Пост",
    )
    image = models.ImageField("Изображение", upload_to="extracurricular/posts/gallery/")
    caption = models.CharField("Подпись", max_length=255, blank=True)
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Галерея поста внешкольного события"
        verbose_name_plural = "Галереи постов внешкольных событий"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.post}: {self.caption or self.pk}"


class ExtracurricularSchedule(models.Model):
    post = models.ForeignKey(
        ExtracurricularPost,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="schedules",
        verbose_name="Пост внешкольного события",
    )
    grade = models.PositiveSmallIntegerField("Класс (1–11)", choices=GRADE_CHOICES)
    title = models.CharField("Название", max_length=255)
    place = models.CharField("Место", max_length=255, blank=True)
    when = models.DateTimeField("Когда")
    is_active = models.BooleanField("Показывать", default=True)
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Расписание внешкольных занятий"
        verbose_name_plural = "Расписание внешкольных занятий"
        ordering = ["when", "grade", "id"]

    def __str__(self) -> str:
        return self.title or f"Schedule #{self.pk}"
