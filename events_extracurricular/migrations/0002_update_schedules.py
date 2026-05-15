from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("events_extracurricular", "0001_initial"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ExtracurricularItineraryItem",
        ),
        migrations.CreateModel(
            name="ExtracurricularSchedule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "post",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="schedules",
                        to="events_extracurricular.extracurricularpost",
                        verbose_name="Пост внешкольного события",
                    ),
                ),
                (
                    "grade",
                    models.PositiveSmallIntegerField(
                        choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5"), (6, "6"), (7, "7"), (8, "8"), (9, "9"), (10, "10"), (11, "11")],
                        verbose_name="Класс (1–11)",
                    ),
                ),
                ("title", models.CharField(max_length=255, verbose_name="Название")),
                ("title_tg", models.CharField(blank=True, max_length=255, null=True, verbose_name="Название [tg]")),
                ("title_ru", models.CharField(blank=True, max_length=255, null=True, verbose_name="Название [ru]")),
                ("title_en", models.CharField(blank=True, max_length=255, null=True, verbose_name="Название [en]")),
                ("place", models.CharField(blank=True, max_length=255, verbose_name="Место")),
                ("place_tg", models.CharField(blank=True, max_length=255, null=True, verbose_name="Место [tg]")),
                ("place_ru", models.CharField(blank=True, max_length=255, null=True, verbose_name="Место [ru]")),
                ("place_en", models.CharField(blank=True, max_length=255, null=True, verbose_name="Место [en]")),
                ("when", models.DateTimeField(verbose_name="Когда")),
                ("is_active", models.BooleanField(default=True, verbose_name="Показывать")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, verbose_name="Создано")),
            ],
            options={
                "verbose_name": "Расписание внешкольных занятий",
                "verbose_name_plural": "Расписание внешкольных занятий",
                "ordering": ["when", "grade", "id"],
            },
        ),
    ]
