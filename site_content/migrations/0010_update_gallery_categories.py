from django.db import migrations, models


def remap_gallery_categories_forward(apps, schema_editor):
    GalleryImage = apps.get_model("site_content", "GalleryImage")
    mapping = {
        "campus": "school",
        "sports": "sport",
        "arts": "educational",
        "stem": "academic",
        "events": "school",
    }
    for old_value, new_value in mapping.items():
        GalleryImage.objects.filter(category=old_value).update(category=new_value)


def remap_gallery_categories_backward(apps, schema_editor):
    GalleryImage = apps.get_model("site_content", "GalleryImage")
    mapping = {
        "school": "campus",
        "sport": "sports",
        "educational": "arts",
        "academic": "stem",
    }
    for old_value, new_value in mapping.items():
        GalleryImage.objects.filter(category=old_value).update(category=new_value)


class Migration(migrations.Migration):
    dependencies = [
        ("site_content", "0009_delete_infrastructureitem"),
    ]

    operations = [
        migrations.RunPython(remap_gallery_categories_forward, remap_gallery_categories_backward),
        migrations.AlterField(
            model_name="galleryimage",
            name="category",
            field=models.CharField(
                choices=[
                    ("school", "School"),
                    ("sport", "Sport"),
                    ("educational", "Educational"),
                    ("academic", "Academic"),
                ],
                default="school",
                max_length=32,
                verbose_name="Категория",
            ),
        ),
    ]
