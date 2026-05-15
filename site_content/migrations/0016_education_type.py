from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("site_content", "0015_students_community"),
    ]

    operations = [
        migrations.CreateModel(
            name="EducationType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255, verbose_name="Название")),
                ("text", models.TextField(blank=True, verbose_name="Описание")),
                ("image", models.ImageField(blank=True, null=True, upload_to="education_types/", verbose_name="Изображение")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Порядок")),
                ("is_active", models.BooleanField(default=True, verbose_name="Показывать")),
            ],
            options={
                "verbose_name": "Тип образования",
                "verbose_name_plural": "Типы образования",
                "ordering": ["order", "id"],
            },
        ),
    ]
