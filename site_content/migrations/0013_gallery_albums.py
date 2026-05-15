from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


def create_gallery_albums(apps, schema_editor):
    GalleryAlbum = apps.get_model("site_content", "GalleryAlbum")
    GalleryImage = apps.get_model("site_content", "GalleryImage")

    category_map = {
        "school": ("school", "Школа"),
        "sport": ("sport", "Спорт"),
        "educational": ("educational", "Образование"),
        "academic": ("academic", "Академическое"),
        "campus": ("school", "Школа"),
        "sports": ("sport", "Спорт"),
        "arts": ("educational", "Образование"),
        "stem": ("academic", "Академическое"),
        "events": ("school", "Школа"),
    }
    order_map = {"school": 0, "sport": 1, "educational": 2, "academic": 3}

    albums: dict[str, models.Model] = {}
    for slug, title in [("school", "Школа"), ("sport", "Спорт"), ("educational", "Образование"), ("academic", "Академическое")]:
        album, _ = GalleryAlbum.objects.get_or_create(
            slug=slug,
            defaults={"title": title, "order": order_map.get(slug, 0), "is_public": True},
        )
        albums[slug] = album

    default_album = albums.get("school")
    if default_album is None:
        default_album = GalleryAlbum.objects.create(
            title="Школа",
            slug="school",
            order=0,
            is_public=True,
        )
        albums["school"] = default_album

    for image in GalleryImage.objects.all():
        category = (getattr(image, "category", None) or "").strip() or "school"
        album_slug, _title = category_map.get(category, ("school", "Школа"))
        album = albums.get(album_slug, default_album)
        if image.album_id != album.id:
            image.album = album
            image.save(update_fields=["album"])


def restore_gallery_categories(apps, schema_editor):
    GalleryImage = apps.get_model("site_content", "GalleryImage")
    slug_map = {
        "school": "school",
        "sport": "sport",
        "educational": "educational",
        "academic": "academic",
    }
    for image in GalleryImage.objects.select_related("album"):
        slug = getattr(getattr(image, "album", None), "slug", "") or "school"
        image.category = slug_map.get(slug, "school")
        image.save(update_fields=["category"])


class Migration(migrations.Migration):
    dependencies = [
        ("site_content", "0012_teachers_committee_models"),
    ]

    operations = [
        migrations.CreateModel(
            name="GalleryAlbum",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255, verbose_name="Название альбома")),
                ("title_tg", models.CharField(max_length=255, null=True, verbose_name="Название альбома")),
                ("title_ru", models.CharField(max_length=255, null=True, verbose_name="Название альбома")),
                ("title_en", models.CharField(max_length=255, null=True, verbose_name="Название альбома")),
                ("slug", models.SlugField(help_text="Используется в URL. Только латиница, цифры и дефисы.", max_length=64, unique=True, verbose_name="Код")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Порядок")),
                ("is_public", models.BooleanField(default=True, verbose_name="Показывать гостям")),
                ("created_at", models.DateTimeField(default=timezone.now, verbose_name="Создано")),
            ],
            options={
                "verbose_name": "Альбом (галерея)",
                "verbose_name_plural": "Альбомы (галерея)",
                "ordering": ["order", "id"],
            },
        ),
        migrations.AddField(
            model_name="galleryimage",
            name="album",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="images",
                to="site_content.galleryalbum",
                verbose_name="Альбом",
            ),
        ),
        migrations.RunPython(create_gallery_albums, restore_gallery_categories),
        migrations.AlterField(
            model_name="galleryimage",
            name="album",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="images",
                to="site_content.galleryalbum",
                verbose_name="Альбом",
            ),
        ),
        migrations.RemoveField(
            model_name="galleryimage",
            name="category",
        ),
    ]
