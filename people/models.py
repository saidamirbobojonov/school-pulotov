from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import pgettext_lazy


class SchoolClass(models.Model):
    name = models.CharField("Класс", max_length=32)
    grade = models.PositiveSmallIntegerField("Ступень (1–11)", default=1)
    is_active = models.BooleanField("Активен", default=True)
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Класс"
        verbose_name_plural = "Классы"
        ordering = ["grade", "name"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(grade__gte=1) & models.Q(grade__lte=11),
                name="class_grade_1_11",
            )
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def display_name(self) -> str:
        name = (self.name or "").strip()
        if any(ch.isdigit() for ch in name):
            return name
        return f"{self.grade}{name}"


class Subject(models.Model):
    name = models.CharField("Предмет", max_length=255)

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Staff(models.Model):
    ROLE_CHOICES = [
        ("founder", pgettext_lazy("staff role", "Founder")),
        ("admin", pgettext_lazy("staff role", "Administration")),
        ("teacher", pgettext_lazy("staff role", "Teachers")),
        ("staff", pgettext_lazy("staff role", "Staff")),
    ]
    order = models.PositiveIntegerField(
        "Порядок",
        default=0,
        help_text="Чем меньше число — тем выше в списке"
    )
    full_name = models.CharField("ФИО", max_length=160)
    role = models.CharField("Категория", max_length=16, choices=ROLE_CHOICES)
    position = models.CharField("Должность", max_length=160, blank=True)
    photo = models.ImageField("Фото", upload_to="team/", blank=True, null=True)
    bio = models.TextField("Описание", blank=True)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="staff_profile",
        verbose_name="Пользователь (логин)",
    )

    subjects = models.ManyToManyField(Subject, blank=True, verbose_name="Предметы")

    created_at = models.DateTimeField("Создано", default=timezone.now)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ["role", "full_name"]

    def __str__(self) -> str:
        return self.full_name

    def clean(self) -> None:
        if self.user and getattr(self.user, "role", None) == "student":
            raise ValidationError("User with role=student cannot be assigned as Staff.")


class Student(models.Model):
    full_name = models.CharField("Полное имя", max_length=255)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, verbose_name="Класс")
    image = models.ImageField("Фото", upload_to="students/", blank=True, null=True)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="student_profile",
        verbose_name="Пользователь (логин)",
    )

    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Ученик"
        verbose_name_plural = "Ученики"
        ordering = ["school_class__grade", "school_class__name", "full_name"]

    def __str__(self) -> str:
        return f"{self.full_name} ({self.school_class})"

    def clean(self) -> None:
        if self.user and getattr(self.user, "role", None) == "teacher":
            raise ValidationError("User with role=teacher cannot be assigned as Student.")


class GraduateDestination(models.Model):
    city = models.CharField("Город", max_length=160)
    country = models.CharField("Страна", max_length=160)
    latitude = models.FloatField("Широта (lat)")
    longitude = models.FloatField("Долгота (lng)")

    title = models.CharField("Заголовок карточки", max_length=255, blank=True)
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Фото/превью", upload_to="graduates/destinations/", blank=True, null=True)

    assistant_url = models.URLField("Ссылка (кнопка)", blank=True)

    is_public = models.BooleanField("Показывать на сайте", default=True)
    created_at = models.DateTimeField("Создано", default=timezone.now)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Локация выпускников (международная)"
        verbose_name_plural = "Локации выпускников (международные)"
        ordering = ["country", "city", "id"]
        indexes = [
            models.Index(fields=["is_public", "country", "city"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(latitude__gte=-90.0) & models.Q(latitude__lte=90.0),
                name="graduate_destination_lat_range",
            ),
            models.CheckConstraint(
                condition=models.Q(longitude__gte=-180.0) & models.Q(longitude__lte=180.0),
                name="graduate_destination_lng_range",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.city}, {self.country}"


class GraduateStudyRecord(models.Model):
    destination = models.ForeignKey(
        GraduateDestination,
        on_delete=models.CASCADE,
        related_name="graduates",
        verbose_name="Локация",
    )
    full_name = models.CharField("ФИО выпускника", max_length=255)
    photo_1 = models.ImageField("Фото 1", upload_to="graduates/records/", blank=True, null=True)
    photo_2 = models.ImageField("Фото 2", upload_to="graduates/records/", blank=True, null=True)
    graduation_year = models.PositiveSmallIntegerField("Год выпуска", blank=True, null=True)
    university_name = models.CharField("Университет", max_length=255)
    program = models.CharField("Программа/специализация", max_length=255, blank=True)
    degree = models.CharField("Степень", max_length=64, blank=True)
    start_year = models.PositiveSmallIntegerField("Год поступления", blank=True, null=True)

    is_public = models.BooleanField("Показывать на сайте", default=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Выпускник за рубежом"
        verbose_name_plural = "Выпускники за рубежом"
        ordering = ["order", "id"]
        indexes = [
            models.Index(fields=["destination", "is_public", "order", "id"]),
        ]

    def __str__(self) -> str:
        uni = (self.university_name or "").strip()
        year = f" ({self.graduation_year})" if self.graduation_year else ""
        return f"{self.full_name}{year} — {uni}"
