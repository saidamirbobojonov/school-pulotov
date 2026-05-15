from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ConstructionPost",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255, verbose_name="Заголовок")),
                ("text", models.TextField(blank=True, verbose_name="Текст")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, verbose_name="Создано")),
            ],
            options={
                "verbose_name": "Пост: Строительство и администрация",
                "verbose_name_plural": "Посты: Строительство и администрация",
                "ordering": ["-created_at", "-id"],
            },
        ),
        migrations.CreateModel(
            name="PerspectiveOverview",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(blank=True, max_length=255, verbose_name="Заголовок")),
                ("text", models.TextField(blank=True, verbose_name="Текст")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлено")),
            ],
            options={
                "verbose_name": "Обзор: Перспектива",
                "verbose_name_plural": "Обзор: Перспектива",
            },
        ),
        migrations.CreateModel(
            name="PerspectiveSection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "section_type",
                    models.CharField(
                        choices=[("academic", "Academic"), ("methodical", "Methodical"), ("educational", "Educational")],
                        max_length=32,
                        verbose_name="Раздел",
                    ),
                ),
                ("title", models.CharField(blank=True, max_length=255, verbose_name="Заголовок")),
                ("text", models.TextField(blank=True, verbose_name="Текст")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлено")),
            ],
            options={
                "verbose_name": "Раздел: Перспектива",
                "verbose_name_plural": "Разделы: Перспектива",
                "ordering": ["section_type", "id"],
            },
        ),
        migrations.CreateModel(
            name="ConstructionGalleryImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "image",
                    models.ImageField(upload_to="perspective/construction/gallery/", verbose_name="Изображение"),
                ),
                ("caption", models.CharField(blank=True, max_length=255, verbose_name="Подпись")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Порядок")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, verbose_name="Создано")),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="gallery",
                        to="perspective.constructionpost",
                        verbose_name="Пост",
                    ),
                ),
            ],
            options={
                "verbose_name": "Галерея: Строительство и администрация",
                "verbose_name_plural": "Галерея: Строительство и администрация",
                "ordering": ["order", "-created_at", "-id"],
            },
        ),
        migrations.AddConstraint(
            model_name="perspectivesection",
            constraint=models.UniqueConstraint(fields=("section_type",), name="uniq_perspective_section_type"),
        ),
    ]
