from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


class Migration(migrations.Migration):
    dependencies = [
        ("site_content", "0011_add_future_gym_zone"),
        ("people", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TeachersCommitteePage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("mission_title", models.CharField(blank=True, max_length=255, verbose_name="Заголовок: Миссия")),
                ("mission_title_tg", models.CharField(blank=True, max_length=255, null=True, verbose_name="Заголовок: Миссия")),
                ("mission_title_ru", models.CharField(blank=True, max_length=255, null=True, verbose_name="Заголовок: Миссия")),
                ("mission_title_en", models.CharField(blank=True, max_length=255, null=True, verbose_name="Заголовок: Миссия")),
                ("mission_text", models.TextField(blank=True, verbose_name="Текст: Миссия (абзац 1)")),
                ("mission_text_tg", models.TextField(blank=True, null=True, verbose_name="Текст: Миссия (абзац 1)")),
                ("mission_text_ru", models.TextField(blank=True, null=True, verbose_name="Текст: Миссия (абзац 1)")),
                ("mission_text_en", models.TextField(blank=True, null=True, verbose_name="Текст: Миссия (абзац 1)")),
                ("mission_text_2", models.TextField(blank=True, verbose_name="Текст: Миссия (абзац 2)")),
                ("mission_text_2_tg", models.TextField(blank=True, null=True, verbose_name="Текст: Миссия (абзац 2)")),
                ("mission_text_2_ru", models.TextField(blank=True, null=True, verbose_name="Текст: Миссия (абзац 2)")),
                ("mission_text_2_en", models.TextField(blank=True, null=True, verbose_name="Текст: Миссия (абзац 2)")),
                ("members_intro", models.TextField(blank=True, verbose_name="Текст: Участники (введение)")),
                ("members_intro_tg", models.TextField(blank=True, null=True, verbose_name="Текст: Участники (введение)")),
                ("members_intro_ru", models.TextField(blank=True, null=True, verbose_name="Текст: Участники (введение)")),
                ("members_intro_en", models.TextField(blank=True, null=True, verbose_name="Текст: Участники (введение)")),
                ("meetings_intro", models.TextField(blank=True, verbose_name="Текст: Собрания (введение)")),
                ("meetings_intro_tg", models.TextField(blank=True, null=True, verbose_name="Текст: Собрания (введение)")),
                ("meetings_intro_ru", models.TextField(blank=True, null=True, verbose_name="Текст: Собрания (введение)")),
                ("meetings_intro_en", models.TextField(blank=True, null=True, verbose_name="Текст: Собрания (введение)")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлено")),
            ],
            options={
                "verbose_name": "Страница: Методический отдел",
                "verbose_name_plural": "Страница: Методический отдел",
            },
        ),
        migrations.CreateModel(
            name="TeachersCommitteeFocusArea",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Порядок")),
                ("icon", models.CharField(default="volunteer_activism", max_length=64, verbose_name="Иконка (Material Symbol)")),
                ("title", models.CharField(max_length=255, verbose_name="Название")),
                ("title_tg", models.CharField(max_length=255, null=True, verbose_name="Название")),
                ("title_ru", models.CharField(max_length=255, null=True, verbose_name="Название")),
                ("title_en", models.CharField(max_length=255, null=True, verbose_name="Название")),
                ("is_active", models.BooleanField(default=True, verbose_name="Показывать")),
                (
                    "page",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="focus_areas",
                        to="site_content.teacherscommitteepage",
                        verbose_name="Страница",
                    ),
                ),
            ],
            options={
                "verbose_name": "Направление работы (метод. отдел)",
                "verbose_name_plural": "Направления работы (метод. отдел)",
                "ordering": ["order", "id"],
            },
        ),
        migrations.CreateModel(
            name="TeachersCommitteeMember",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Порядок")),
                ("role_title", models.CharField(blank=True, max_length=255, verbose_name="Роль")),
                ("role_title_tg", models.CharField(blank=True, max_length=255, null=True, verbose_name="Роль")),
                ("role_title_ru", models.CharField(blank=True, max_length=255, null=True, verbose_name="Роль")),
                ("role_title_en", models.CharField(blank=True, max_length=255, null=True, verbose_name="Роль")),
                ("is_active", models.BooleanField(default=True, verbose_name="Показывать")),
                (
                    "page",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="members",
                        to="site_content.teacherscommitteepage",
                        verbose_name="Страница",
                    ),
                ),
                (
                    "staff",
                    models.ForeignKey(
                        limit_choices_to={"role": "teacher"},
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="teachers_committee_memberships",
                        to="people.staff",
                        verbose_name="Учитель",
                    ),
                ),
            ],
            options={
                "verbose_name": "Участник (метод. отдел)",
                "verbose_name_plural": "Участники (метод. отдел)",
                "ordering": ["order", "id"],
            },
        ),
        migrations.CreateModel(
            name="TeachersCommitteeMeeting",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("start_at", models.DateTimeField(default=timezone.now, verbose_name="Начало")),
                ("end_at", models.DateTimeField(blank=True, null=True, verbose_name="Окончание")),
                ("location", models.CharField(blank=True, max_length=255, verbose_name="Место")),
                ("location_tg", models.CharField(blank=True, max_length=255, null=True, verbose_name="Место")),
                ("location_ru", models.CharField(blank=True, max_length=255, null=True, verbose_name="Место")),
                ("location_en", models.CharField(blank=True, max_length=255, null=True, verbose_name="Место")),
                ("location_icon", models.CharField(default="meeting_room", max_length=64, verbose_name="Иконка места (Material Symbol)")),
                ("location_url", models.URLField(blank=True, verbose_name="Ссылка на место/Zoom")),
                ("agenda_topic", models.CharField(blank=True, max_length=255, verbose_name="Тема")),
                ("agenda_topic_tg", models.CharField(blank=True, max_length=255, null=True, verbose_name="Тема")),
                ("agenda_topic_ru", models.CharField(blank=True, max_length=255, null=True, verbose_name="Тема")),
                ("agenda_topic_en", models.CharField(blank=True, max_length=255, null=True, verbose_name="Тема")),
                ("rsvp_url", models.URLField(blank=True, verbose_name="Ссылка RSVP")),
                ("is_active", models.BooleanField(default=True, verbose_name="Показывать")),
                (
                    "page",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="meetings",
                        to="site_content.teacherscommitteepage",
                        verbose_name="Страница",
                    ),
                ),
            ],
            options={
                "verbose_name": "Собрание (метод. отдел)",
                "verbose_name_plural": "Собрания (метод. отдел)",
                "ordering": ["start_at", "id"],
            },
        ),
    ]
