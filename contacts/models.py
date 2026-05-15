from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import pgettext_lazy


class ContactPage(models.Model):
    address = models.CharField("Адрес", max_length=255)
    address_2 = models.CharField("Адрес-2", max_length=255, blank=True)
    working_hours = models.CharField("Рабочие часы", max_length=255, blank=True)
    phone = models.CharField("Телефон", max_length=64, blank=True)
    phone_2 = models.CharField("Телефон (доп.)", max_length=64, blank=True)
    email = models.EmailField("Email", blank=True)
    email_2 = models.EmailField("Email (доп.)", blank=True)
    map_iframe_src = models.URLField("Ссылка на карту", blank=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Контакты — страница"
        verbose_name_plural = "Контакты — страница"

    def __str__(self) -> str:
        return "Contact Page"

    def save(self, *args, **kwargs) -> None:
        if not self.pk and ContactPage.objects.exists():
            raise ValidationError("Можно создать только одну запись ContactPage.")
        super().save(*args, **kwargs)


class ContactMessage(models.Model):
    name = models.CharField("Имя", max_length=160)
    phone = models.CharField("Телефон", max_length=64)
    email = models.EmailField("Email", blank=True)
    subject = models.CharField("Тема", max_length=160, blank=True)
    message = models.TextField("Сообщение")
    created_at = models.DateTimeField("Создано", default=timezone.now)
    is_read = models.BooleanField("Прочитано", default=False)

    class Meta:
        verbose_name = "Сообщение с формы"
        verbose_name_plural = "Сообщения с формы"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} — {self.subject or 'Без темы'}"


class AdmissionApplication(models.Model):
    class Status(models.TextChoices):
        NEW = "new", pgettext_lazy("admission status", "New")
        IN_PROGRESS = "in_progress", pgettext_lazy("admission status", "In progress")
        DONE = "done", pgettext_lazy("admission status", "Done")

    student_name = models.CharField("Ученик", max_length=160)
    parent_name = models.CharField("Родитель/опекун", max_length=160)
    phone = models.CharField("Телефон", max_length=64)
    email = models.EmailField("Email", blank=True)
    grade = models.PositiveSmallIntegerField("Класс (1–11)")
    note = models.TextField("Комментарий", blank=True)

    status = models.CharField("Статус", max_length=16, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Заявка на поступление"
        verbose_name_plural = "Заявки на поступление"
        ordering = ["-created_at", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(grade__gte=1) & models.Q(grade__lte=11),
                name="admission_grade_1_11",
            )
        ]

    def __str__(self) -> str:
        return f"{self.student_name} → {self.grade}"


class AdmissionApplicationDocument(models.Model):
    application = models.ForeignKey(
        AdmissionApplication,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name="Заявка",
    )
    file = models.FileField("Файл", upload_to="admissions/documents/%Y/%m/")
    original_name = models.CharField("Оригинальное имя", max_length=255, blank=True)
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Документ заявки"
        verbose_name_plural = "Документы заявок"
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return self.original_name or (self.file.name if self.file else f"Document #{self.pk}")
