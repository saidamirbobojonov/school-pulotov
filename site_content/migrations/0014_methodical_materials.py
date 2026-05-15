from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("site_content", "0013_gallery_albums"),
    ]

    operations = [
        migrations.CreateModel(
            name="MethodicalMaterial",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255, verbose_name="Название")),
                ("file", models.FileField(upload_to="methodical_materials/", verbose_name="Файл")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, verbose_name="Создано")),
            ],
            options={
                "verbose_name": "Методический материал",
                "verbose_name_plural": "Методические материалы",
                "ordering": ["-created_at", "-id"],
            },
        ),
    ]
