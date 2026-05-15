from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import pgettext_lazy


class SchoolName(models.Model):
    name = models.CharField("Имя школы", max_length=255)
    image = models.ImageField("Лого", upload_to="logo/", blank=True, null=True)

    class Meta:
        verbose_name = "Информация про школу"
        verbose_name_plural = "Информация про школу"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        if not self.pk and SchoolName.objects.exists():
            raise ValidationError("Можно создать только одну запись SchoolName.")
        super().save(*args, **kwargs)


class SchoolContent(models.Model):
    big_info_title = models.CharField("Заголовок: О школе", max_length=255, blank=True)
    big_info_text = models.TextField("Большой текст: О школе", blank=True)
    info_image = models.ImageField("фото", upload_to="info/", blank=True, null=True)

    history_title = models.CharField("Заголовок: История", max_length=255, blank=True)
    history_text = models.TextField("Большой текст: История школы", blank=True)
    history_image = models.ImageField("фото", upload_to="info/", blank=True, null=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Контент школы (О школе / История)"
        verbose_name_plural = "Контент школы (О школе / История)"

    def __str__(self) -> str:
        return "School Content"

    def save(self, *args, **kwargs) -> None:
        if not self.pk and SchoolContent.objects.exists():
            raise ValidationError("Можно создать только одну запись SchoolContent.")
        super().save(*args, **kwargs)


class SocialNetwork(models.Model):
    svg = models.TextField("SVG", blank=True, null=True)
    link = models.URLField("Ссылка", max_length=255)
    order = models.PositiveIntegerField("Порядок", default=0)
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Социальная сеть"
        verbose_name_plural = "Социальные сети"
        ordering = ["order", "created_at"]

    def __str__(self) -> str:
        return self.link


class Hero(models.Model):
    menu_item = models.ForeignKey(
        "navigation.MenuItem",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="heroes",
        verbose_name="Пункт меню",
    )
    title = models.CharField("Заголовок", max_length=255, blank=True)
    text = models.TextField("Текст", blank=True)
    bg_image = models.ImageField("Фоновое изображение", upload_to="hero/", blank=True, null=True)
    bg_video = models.FileField("Фоновое видео", upload_to="hero/videos/", blank=True, null=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Герой блок"
        verbose_name_plural = "Герой блоки"
        ordering = ["order", "id"]

    def clean(self) -> None:
        if self.bg_image and self.bg_video:
            raise ValidationError("Загрузите либо изображение, либо видео, но не оба сразу.")

    def __str__(self) -> str:
        return self.title or f"Hero #{self.pk}"


class Announcement(models.Model):
    title = models.CharField("Заголовок", max_length=255)
    start_at = models.DateTimeField("Начало", default=timezone.now)
    end_at = models.DateTimeField("Окончание", blank=True, null=True)
    body = models.TextField("Текст", blank=True)

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ["-start_at", "-id"]

    def __str__(self) -> str:
        return self.title

    def is_active(self) -> bool:
        now = timezone.now()
        if self.end_at:
            return self.start_at <= now <= self.end_at
        return self.start_at <= now

    is_active.boolean = True
    is_active.short_description = "Активно"


class GalleryAlbum(models.Model):
    title = models.CharField("Название альбома", max_length=255)
    slug = models.SlugField(
        "Код",
        max_length=64,
        unique=True,
        help_text="Используется в URL. Только латиница, цифры и дефисы.",
    )
    order = models.PositiveIntegerField("Порядок", default=0)
    is_public = models.BooleanField("Показывать гостям", default=True)
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Альбом (галерея)"
        verbose_name_plural = "Альбомы (галерея)"
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.title or f"Album #{self.pk}"


class GalleryImage(models.Model):
    album = models.ForeignKey(
        GalleryAlbum,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Альбом",
    )
    image = models.ImageField("Изображение", upload_to="gallery/")
    caption = models.CharField("Подпись", max_length=255, blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_public = models.BooleanField("Показывать гостям", default=True)
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Фото (галерея)"
        verbose_name_plural = "Фото (галерея)"
        ordering = ["album__order", "order", "-created_at", "-id"]

    def __str__(self) -> str:
        return self.caption or f"GalleryImage #{self.pk}"


class FAQItem(models.Model):
    question = models.CharField("Вопрос", max_length=255)
    answer = models.TextField("Ответ", blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показывать гостям", default=True)
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.question


class Slogan(models.Model):
    title = models.CharField("Заголовок", max_length=255)
    text = models.TextField("Текст", blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показывать гостям", default=True)
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Слоган / Ценность"
        verbose_name_plural = "Слоганы / Ценности"
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.title or f"Slogan #{self.pk}"


class AdmissionsPage(models.Model):
    hero_title = models.CharField("Заголовок (Admissions)", max_length=255, blank=True)
    hero_text = models.TextField("Текст (Admissions)", blank=True)

    process_title = models.CharField("Заголовок: Процесс", max_length=255, blank=True)
    process_text = models.TextField("Подзаголовок: Процесс", blank=True)

    form_title = models.CharField("Заголовок: Форма", max_length=255, blank=True)
    application_pdf = models.FileField(
        "PDF для поступления",
        upload_to="admissions/",
        blank=True,
        null=True,
        help_text="Файл будет доступен на странице /admissions/ для предпросмотра и скачивания.",
    )

    dates_title = models.CharField("Заголовок: Даты", max_length=255, blank=True)

    questions_title = models.CharField("Заголовок: Вопросы", max_length=255, blank=True)
    questions_text = models.TextField("Текст: Вопросы", blank=True)
    office_email = models.EmailField("Email приемной комиссии", blank=True)

    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Страница: Поступление"
        verbose_name_plural = "Страница: Поступление"

    def __str__(self) -> str:
        return "Admissions Page"


class MethodicalMaterial(models.Model):
    title = models.CharField("Название", max_length=255)
    file = models.FileField("Файл", upload_to="methodical_materials/")
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Методический материал"
        verbose_name_plural = "Методические материалы"
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return self.title or f"Материал #{self.pk}"


class EducationType(models.Model):
    title = models.CharField("Название", max_length=255)
    text = models.TextField("Описание", blank=True)
    image = models.ImageField("Изображение", upload_to="education_types/", blank=True, null=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показывать", default=True)

    class Meta:
        verbose_name = "Тип образования"
        verbose_name_plural = "Типы образования"
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.title or f"EducationType #{self.pk}"


class AdmissionStep(models.Model):
    page = models.ForeignKey(
        AdmissionsPage,
        on_delete=models.CASCADE,
        related_name="steps",
        verbose_name="Страница",
    )
    order = models.PositiveIntegerField("Порядок", default=0)
    icon = models.CharField("Иконка (Material Symbol)", max_length=64, default="task_alt")
    title = models.CharField("Заголовок", max_length=255)
    description = models.TextField("Описание", blank=True)

    class Meta:
        verbose_name = "Шаг поступления"
        verbose_name_plural = "Шаги поступления"
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.title


class AdmissionImportantDate(models.Model):
    page = models.ForeignKey(
        AdmissionsPage,
        on_delete=models.CASCADE,
        related_name="important_dates",
        verbose_name="Страница",
    )
    order = models.PositiveIntegerField("Порядок", default=0)
    label = models.CharField("Заголовок (верхняя строка)", max_length=255)
    date_text = models.CharField("Дата (текст)", max_length=255)
    is_active = models.BooleanField("Выделять", default=True)

    class Meta:
        verbose_name = "Важная дата (поступление)"
        verbose_name_plural = "Важные даты (поступление)"
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.label


class ParentsCommitteePage(models.Model):
    mission_title = models.CharField("Заголовок: Миссия", max_length=255, blank=True)
    mission_text = models.TextField("Текст: Миссия (абзац 1)", blank=True)
    mission_text_2 = models.TextField("Текст: Миссия (абзац 2)", blank=True)

    members_intro = models.TextField("Текст: Участники (введение)", blank=True)
    meetings_intro = models.TextField("Текст: Собрания (введение)", blank=True)

    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Страница: Родительский комитет"
        verbose_name_plural = "Страница: Родительский комитет"

    def __str__(self) -> str:
        return "Parents Committee Page"

    def save(self, *args, **kwargs) -> None:
        if not self.pk and ParentsCommitteePage.objects.exists():
            raise ValidationError("Можно создать только одну запись ParentsCommitteePage.")
        super().save(*args, **kwargs)


class ParentsCommitteeFocusArea(models.Model):
    page = models.ForeignKey(
        ParentsCommitteePage,
        on_delete=models.CASCADE,
        related_name="focus_areas",
        verbose_name="Страница",
    )
    order = models.PositiveIntegerField("Порядок", default=0)
    icon = models.CharField("Иконка (Material Symbol)", max_length=64, default="volunteer_activism")
    title = models.CharField("Название", max_length=255)
    is_active = models.BooleanField("Показывать", default=True)

    class Meta:
        verbose_name = "Направление работы (род. комитет)"
        verbose_name_plural = "Направления работы (род. комитет)"
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.title or f"FocusArea #{self.pk}"


class ParentsCommitteeMember(models.Model):
    page = models.ForeignKey(
        ParentsCommitteePage,
        on_delete=models.CASCADE,
        related_name="members",
        verbose_name="Страница",
    )
    order = models.PositiveIntegerField("Порядок", default=0)
    full_name = models.CharField("ФИО", max_length=255)
    role = models.CharField("Роль", max_length=255, blank=True)
    photo = models.ImageField("Фото", upload_to="parents_committee/members/", blank=True, null=True)
    is_active = models.BooleanField("Показывать", default=True)

    class Meta:
        verbose_name = "Участник (род. комитет)"
        verbose_name_plural = "Участники (род. комитет)"
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.full_name or f"Member #{self.pk}"


class ParentsCommitteeMeeting(models.Model):
    page = models.ForeignKey(
        ParentsCommitteePage,
        on_delete=models.CASCADE,
        related_name="meetings",
        verbose_name="Страница",
    )
    start_at = models.DateTimeField("Начало", default=timezone.now)
    end_at = models.DateTimeField("Окончание", blank=True, null=True)
    location = models.CharField("Место", max_length=255, blank=True)
    location_icon = models.CharField("Иконка места (Material Symbol)", max_length=64, default="meeting_room")
    location_url = models.URLField("Ссылка на место/Zoom", blank=True)
    agenda_topic = models.CharField("Тема", max_length=255, blank=True)
    rsvp_url = models.URLField("Ссылка RSVP", blank=True)
    is_active = models.BooleanField("Показывать", default=True)

    class Meta:
        verbose_name = "Собрание (род. комитет)"
        verbose_name_plural = "Собрания (род. комитет)"
        ordering = ["start_at", "id"]

    def __str__(self) -> str:
        date_text = self.start_at.strftime("%Y-%m-%d") if self.start_at else ""
        return self.agenda_topic or date_text or f"Meeting #{self.pk}"


class TeachersCommitteePage(models.Model):
    mission_title = models.CharField("Заголовок: Миссия", max_length=255, blank=True)
    mission_text = models.TextField("Текст: Миссия (абзац 1)", blank=True)
    mission_text_2 = models.TextField("Текст: Миссия (абзац 2)", blank=True)

    members_intro = models.TextField("Текст: Участники (введение)", blank=True)
    meetings_intro = models.TextField("Текст: Собрания (введение)", blank=True)

    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Страница: Методический отдел"
        verbose_name_plural = "Страница: Методический отдел"

    def __str__(self) -> str:
        return "Teachers Committee Page"

    def save(self, *args, **kwargs) -> None:
        if not self.pk and TeachersCommitteePage.objects.exists():
            raise ValidationError("Можно создать только одну запись TeachersCommitteePage.")
        super().save(*args, **kwargs)


class TeachersCommitteeFocusArea(models.Model):
    page = models.ForeignKey(
        TeachersCommitteePage,
        on_delete=models.CASCADE,
        related_name="focus_areas",
        verbose_name="Страница",
    )
    order = models.PositiveIntegerField("Порядок", default=0)
    icon = models.CharField("Иконка (Material Symbol)", max_length=64, default="volunteer_activism")
    title = models.CharField("Название", max_length=255)
    is_active = models.BooleanField("Показывать", default=True)

    class Meta:
        verbose_name = "Направление работы (метод. отдел)"
        verbose_name_plural = "Направления работы (метод. отдел)"
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.title or f"FocusArea #{self.pk}"


class TeachersCommitteeMember(models.Model):
    page = models.ForeignKey(
        TeachersCommitteePage,
        on_delete=models.CASCADE,
        related_name="members",
        verbose_name="Страница",
    )
    order = models.PositiveIntegerField("Порядок", default=0)
    staff = models.ForeignKey(
        "people.Staff",
        on_delete=models.CASCADE,
        related_name="teachers_committee_memberships",
        verbose_name="Учитель",
        limit_choices_to={"role": "teacher"},
    )
    role_title = models.CharField("Роль", max_length=255, blank=True)
    is_active = models.BooleanField("Показывать", default=True)

    class Meta:
        verbose_name = "Участник (метод. отдел)"
        verbose_name_plural = "Участники (метод. отдел)"
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return getattr(self.staff, "full_name", "") or f"Member #{self.pk}"


class TeachersCommitteeMeeting(models.Model):
    page = models.ForeignKey(
        TeachersCommitteePage,
        on_delete=models.CASCADE,
        related_name="meetings",
        verbose_name="Страница",
    )
    start_at = models.DateTimeField("Начало", default=timezone.now)
    end_at = models.DateTimeField("Окончание", blank=True, null=True)
    location = models.CharField("Место", max_length=255, blank=True)
    location_icon = models.CharField("Иконка места (Material Symbol)", max_length=64, default="meeting_room")
    location_url = models.URLField("Ссылка на место/Zoom", blank=True)
    agenda_topic = models.CharField("Тема", max_length=255, blank=True)
    rsvp_url = models.URLField("Ссылка RSVP", blank=True)
    is_active = models.BooleanField("Показывать", default=True)

    class Meta:
        verbose_name = "Собрание (метод. отдел)"
        verbose_name_plural = "Собрания (метод. отдел)"
        ordering = ["start_at", "id"]

    def __str__(self) -> str:
        date_text = self.start_at.strftime("%Y-%m-%d") if self.start_at else ""
        return self.agenda_topic or date_text or f"Meeting #{self.pk}"


class StudentsCommunityPage(models.Model):
    mission_title = models.CharField("Заголовок: Миссия", max_length=255, blank=True)
    mission_text = models.TextField("Текст: Миссия (абзац 1)", blank=True)
    mission_text_2 = models.TextField("Текст: Миссия (абзац 2)", blank=True)

    members_intro = models.TextField("Текст: Участники (введение)", blank=True)

    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Страница: Сообщество учеников"
        verbose_name_plural = "Страница: Сообщество учеников"

    def __str__(self) -> str:
        return "Students Community Page"

    def save(self, *args, **kwargs) -> None:
        if not self.pk and StudentsCommunityPage.objects.exists():
            raise ValidationError("Можно создать только одну запись StudentsCommunityPage.")
        super().save(*args, **kwargs)


class StudentsCommunityMember(models.Model):
    page = models.ForeignKey(
        StudentsCommunityPage,
        on_delete=models.CASCADE,
        related_name="members",
        verbose_name="Страница",
    )
    order = models.PositiveIntegerField("Порядок", default=0)
    student = models.ForeignKey(
        "people.Student",
        on_delete=models.CASCADE,
        related_name="students_community_memberships",
        verbose_name="Ученик",
    )
    role_title = models.CharField("Роль", max_length=255, blank=True)
    is_active = models.BooleanField("Показывать", default=True)

    class Meta:
        verbose_name = "Участник (сообщество учеников)"
        verbose_name_plural = "Участники (сообщество учеников)"
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return getattr(self.student, "full_name", "") or f"Member #{self.pk}"


class CampusMapZone(models.Model):
    ZONE_CHOICES = [
        ("under-construction", pgettext_lazy("campus zone", "Under Construction")),
        ("future-buildings", pgettext_lazy("campus zone", "Future Buildings")),
        ("future-gym", pgettext_lazy("campus zone", "Future Building (Gym)")),
        ("not-school-territory", pgettext_lazy("campus zone", "Not School Territory")),
        ("entrance", pgettext_lazy("campus zone", "Entrance")),
        ("main-building", pgettext_lazy("campus zone", "Main Building")),
        ("yard", pgettext_lazy("campus zone", "Yard")),
        ("trees-garden", pgettext_lazy("campus zone", "Trees Garden")),
        ("football-stadium", pgettext_lazy("campus zone", "Football Stadium")),
    ]

    zone = models.CharField(
        "Ключ зоны",
        max_length=64,
        choices=ZONE_CHOICES,
        unique=True,
        help_text="Одна запись на каждую зону карты.",
    )
    title = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Изображение", upload_to="campus_map/zones/", blank=True, null=True)

    x_pct = models.DecimalField("X (%)", max_digits=6, decimal_places=2, default=0)
    y_pct = models.DecimalField("Y (%)", max_digits=6, decimal_places=2, default=0)
    width_pct = models.DecimalField("Ширина (%)", max_digits=6, decimal_places=2, default=10)
    height_pct = models.DecimalField("Высота (%)", max_digits=6, decimal_places=2, default=10)

    order = models.PositiveIntegerField("Порядок", default=0)
    is_public = models.BooleanField("Показывать гостям", default=True)
    show_in_buttons = models.BooleanField("Показывать в кнопках", default=True)
    is_clickable = models.BooleanField("Кликабельно", default=True)
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Зона карты кампуса"
        verbose_name_plural = "Зоны карты кампуса"
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.title or self.zone

    def save(self, *args, **kwargs):
        if self.zone == "not-school-territory":
            self.is_clickable = False
        super().save(*args, **kwargs)


class CampusMapZonePart(models.Model):
    zone = models.ForeignKey(
        CampusMapZone,
        on_delete=models.CASCADE,
        related_name="parts",
        verbose_name="Зона",
    )
    order = models.PositiveIntegerField("Порядок", default=0)
    title = models.CharField("Название части", max_length=255)
    description = models.TextField("Описание части", blank=True)
    image = models.ImageField("Изображение части", upload_to="campus_map/parts/", blank=True, null=True)
    is_public = models.BooleanField("Показывать", default=True)

    class Meta:
        verbose_name = "Часть зоны кампуса"
        verbose_name_plural = "Части зон кампуса"
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.title or f"ZonePart #{self.pk}"
