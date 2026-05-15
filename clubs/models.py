from __future__ import annotations

from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from people.models import Staff



class Club(models.Model):
    name = models.CharField("Название", max_length=160)
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Изображение", upload_to="clubs/", blank=True, null=True)

    leader = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Руководитель",
        limit_choices_to={"role": "teacher"},
    )

    schedule_text = models.TextField("Расписание (текст)", blank=True)
    is_public = models.BooleanField("Показывать гостям", default=True)

    slug = models.SlugField("Слаг", max_length=180, unique=True, blank=True)
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Кружок/секция"
        verbose_name_plural = "Кружки/секции"
        ordering = ["name"]

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            base = slugify(self.name)[:160] or "club"
            slug = base
            counter = 2
            while Club.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class ClubGallery(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="gallery", verbose_name="Кружок/секция")
    image = models.ImageField("Изображение", upload_to="clubs/gallery/")
    caption = models.CharField("Подпись", max_length=255, blank=True)
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Галерея кружка/секции"
        verbose_name_plural = "Галереи кружков/секций"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.club}: {self.caption or self.pk}"
