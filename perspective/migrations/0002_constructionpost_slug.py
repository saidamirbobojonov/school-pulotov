from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("perspective", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="constructionpost",
            name="slug",
            field=models.SlugField(blank=True, max_length=220, unique=True, verbose_name="Слаг"),
        ),
    ]
