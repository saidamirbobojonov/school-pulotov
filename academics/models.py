from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import pgettext_lazy

from people.models import SchoolClass, Staff, Subject

GRADE_CHOICES = [(grade, str(grade)) for grade in range(1, 12)]


class Room(models.Model):
    name = models.CharField("Кабинет/аудитория", max_length=64)
    floor = models.CharField("Этаж", max_length=16, blank=True)

    class Meta:
        verbose_name = "Кабинет"
        verbose_name_plural = "Кабинеты"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class TimeSlot(models.Model):
    number = models.PositiveSmallIntegerField("№ урока", unique=True)
    start_time = models.TimeField("Начало")
    end_time = models.TimeField("Конец")

    class Meta:
        verbose_name = "Слот времени"
        verbose_name_plural = "Слоты времени"
        ordering = ["number"]

    def __str__(self) -> str:
        return f"{self.number}: {self.start_time}-{self.end_time}"


class ClassLesson(models.Model):
    WEEKDAY_CHOICES = [
        (1, pgettext_lazy("weekday", "Monday")),
        (2, pgettext_lazy("weekday", "Tuesday")),
        (3, pgettext_lazy("weekday", "Wednesday")),
        (4, pgettext_lazy("weekday", "Thursday")),
        (5, pgettext_lazy("weekday", "Friday")),
        (6, pgettext_lazy("weekday", "Saturday")),
        (7, pgettext_lazy("weekday", "Sunday")),
    ]

    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, verbose_name="Класс")
    weekday = models.PositiveSmallIntegerField("День недели", choices=WEEKDAY_CHOICES)
    slot = models.ForeignKey(TimeSlot, on_delete=models.PROTECT, verbose_name="Время (урок)")
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, verbose_name="Предмет")
    teacher = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Учитель",
        limit_choices_to={"role": "teacher"},
    )
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Кабинет")

    is_public = models.BooleanField("Показывать гостям", default=True)
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Расписание урока"
        verbose_name_plural = "Расписание уроков"
        ordering = ["school_class__grade", "school_class__name", "weekday", "slot__number"]
        constraints = [
            models.UniqueConstraint(fields=["school_class", "weekday", "slot"], name="uniq_class_weekday_slot")
        ]

    def __str__(self) -> str:
        return f"{self.school_class} / {self.get_weekday_display()} / {self.slot} / {self.subject}"


class LessonPlan(models.Model):
    grade = models.PositiveSmallIntegerField("Класс (1–11)", choices=GRADE_CHOICES)
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, verbose_name="Предмет")
    teacher = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Ответственный учитель",
        limit_choices_to={"role": "teacher"},
    )

    title = models.CharField("Тема/название", max_length=255)
    date = models.DateField("Дата", blank=True, null=True)
    description = models.TextField("Описание", blank=True)

    is_published = models.BooleanField("Опубликовано", default=True)

    created_at = models.DateTimeField("Создано", default=timezone.now)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "План урока"
        verbose_name_plural = "Планы уроков"
        ordering = ["-date", "-created_at", "grade", "subject__name"]

    def __str__(self) -> str:
        return f"{self.grade} / {self.subject} / {self.title}"


class LessonMaterial(models.Model):
    lesson_plan = models.ForeignKey(LessonPlan, on_delete=models.CASCADE, related_name="materials", verbose_name="План")
    title = models.CharField("Название", max_length=255, blank=True)

    file = models.FileField("Файл", upload_to="lesson_materials/files/", blank=True, null=True)
    youtube_link = models.URLField("YouTube", blank=True, null=True)
    external_link = models.URLField("Ссылка", blank=True, null=True)

    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Материал урока"
        verbose_name_plural = "Материалы уроков"
        ordering = ["-created_at"]

    def clean(self) -> None:
        if not self.file and not self.youtube_link and not self.external_link:
            raise ValidationError("Добавьте файл или ссылку (YouTube/внешнюю).")

    def __str__(self) -> str:
        return self.title or f"Материал #{self.pk}"


class ClassAssignment(models.Model):
    grade = models.PositiveSmallIntegerField("Класс (1–11)", choices=GRADE_CHOICES)
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Предмет")
    teacher = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Учитель",
        limit_choices_to={"role": "teacher"},
    )

    title = models.CharField("Название задания", max_length=255)
    description = models.TextField("Описание", blank=True)

    assigned_at = models.DateField("Дата выдачи", blank=True, null=True)
    due_at = models.DateField("Сдать до", blank=True, null=True)

    is_published = models.BooleanField("Опубликовано", default=True)

    created_at = models.DateTimeField("Создано", default=timezone.now)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Дополнительное задание"
        verbose_name_plural = "Дополнительные задания"
        ordering = ["-assigned_at", "-created_at"]

    def __str__(self) -> str:
        return f"{self.grade}: {self.title}"


class AssignmentMaterial(models.Model):
    assignment = models.ForeignKey(ClassAssignment, on_delete=models.CASCADE, related_name="materials", verbose_name="Задание")
    title = models.CharField("Название", max_length=255, blank=True)

    file = models.FileField("Файл", upload_to="assignments/files/", blank=True, null=True)
    youtube_link = models.URLField("YouTube", blank=True, null=True)
    external_link = models.URLField("Ссылка", blank=True, null=True)

    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Материал задания"
        verbose_name_plural = "Материалы заданий"
        ordering = ["-created_at"]

    def clean(self) -> None:
        if not self.file and not self.youtube_link and not self.external_link:
            raise ValidationError("Добавьте файл или ссылку (YouTube/внешнюю).")

    def __str__(self) -> str:
        return self.title or f"Материал #{self.pk}"
