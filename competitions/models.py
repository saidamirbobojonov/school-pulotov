from __future__ import annotations

from django.db import models
from django.utils import timezone
from django.utils.translation import pgettext_lazy

from people.models import Student, Subject


class CompetitionType(models.Model):
    name = models.CharField("Тип соревнования", max_length=120, unique=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Тип соревнования"
        verbose_name_plural = "Типы соревнований"
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return self.name


class CompetitionResult(models.Model):
    LEVEL_CHOICES = [
        ("school", pgettext_lazy("competition level", "School")),
        ("city", pgettext_lazy("competition level", "City")),
        ("region", pgettext_lazy("competition level", "Regional")),
        ("republic", pgettext_lazy("competition level", "Republic")),
        ("international", pgettext_lazy("competition level", "International")),
    ]

    competition_type = models.ForeignKey(CompetitionType, on_delete=models.PROTECT, verbose_name="Тип")
    title = models.CharField("Название соревнования", max_length=255)
    year = models.PositiveIntegerField("Год", default=2025)

    level = models.CharField("Уровень", max_length=32, choices=LEVEL_CHOICES, default="school")
    location = models.CharField("Где проходил (место)", max_length=255, blank=True)

    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Ученик")
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Предмет/дисциплина",
    )

    result_place = models.CharField("Результат/место", max_length=64, blank=True)
    description = models.TextField("Описание", blank=True)

    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Результат соревнования"
        verbose_name_plural = "Результаты соревнований"
        ordering = ["-year", "level", "competition_type__order", "title"]

    def __str__(self) -> str:
        return f"{self.student} — {self.title} ({self.get_level_display()}, {self.year})"


class SchoolHonor(models.Model):
    title = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)

    year = models.PositiveIntegerField("Год", default=2025)
    icon = models.CharField("Иконка (Material Symbol)", max_length=64, default="workspace_premium")
    image = models.ImageField("Изображение", upload_to="school_honors/", blank=True, null=True)

    order = models.PositiveIntegerField("Порядок", default=0)
    is_public = models.BooleanField("Показывать гостям", default=True)
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Награда школы"
        verbose_name_plural = "Награды школы"
        ordering = ["order", "-year", "-created_at", "-id"]

    def __str__(self) -> str:
        return f"{self.title} ({self.year})"
