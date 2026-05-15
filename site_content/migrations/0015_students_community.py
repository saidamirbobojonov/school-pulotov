from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("site_content", "0014_methodical_materials"),
    ]

    operations = [
        migrations.CreateModel(
            name="StudentsCommunityPage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("mission_title", models.CharField(blank=True, max_length=255, verbose_name="Заголовок: Миссия")),
                ("mission_text", models.TextField(blank=True, verbose_name="Текст: Миссия (абзац 1)")),
                ("mission_text_2", models.TextField(blank=True, verbose_name="Текст: Миссия (абзац 2)")),
                ("members_intro", models.TextField(blank=True, verbose_name="Текст: Участники (введение)")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлено")),
            ],
            options={
                "verbose_name": "Страница: Сообщество учеников",
                "verbose_name_plural": "Страница: Сообщество учеников",
            },
        ),
        migrations.CreateModel(
            name="StudentsCommunityMember",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Порядок")),
                ("role_title", models.CharField(blank=True, max_length=255, verbose_name="Роль")),
                ("is_active", models.BooleanField(default=True, verbose_name="Показывать")),
                (
                    "page",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="members",
                        to="site_content.studentscommunitypage",
                        verbose_name="Страница",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="students_community_memberships",
                        to="people.student",
                        verbose_name="Ученик",
                    ),
                ),
            ],
            options={
                "verbose_name": "Участник (сообщество учеников)",
                "verbose_name_plural": "Участники (сообщество учеников)",
                "ordering": ["order", "id"],
            },
        ),
    ]
