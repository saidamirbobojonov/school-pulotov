from django.db import migrations


def backfill_campus_map_i18n(apps, schema_editor):
    CampusMapZone = apps.get_model("site_content", "CampusMapZone")
    CampusMapZonePart = apps.get_model("site_content", "CampusMapZonePart")

    for zone in CampusMapZone.objects.all():
        if zone.title:
            zone.title_tg = zone.title_tg or zone.title
            zone.title_ru = zone.title_ru or zone.title
            zone.title_en = zone.title_en or zone.title
        if zone.description:
            zone.description_tg = zone.description_tg or zone.description
            zone.description_ru = zone.description_ru or zone.description
            zone.description_en = zone.description_en or zone.description
        zone.save(
            update_fields=[
                "title_tg",
                "title_ru",
                "title_en",
                "description_tg",
                "description_ru",
                "description_en",
            ]
        )

    for part in CampusMapZonePart.objects.all():
        if part.title:
            part.title_tg = part.title_tg or part.title
            part.title_ru = part.title_ru or part.title
            part.title_en = part.title_en or part.title
        if part.description:
            part.description_tg = part.description_tg or part.description
            part.description_ru = part.description_ru or part.description
            part.description_en = part.description_en or part.description
        part.save(
            update_fields=[
                "title_tg",
                "title_ru",
                "title_en",
                "description_tg",
                "description_ru",
                "description_en",
            ]
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("site_content", "0003_seed_campus_map"),
    ]

    operations = [
        migrations.RunPython(backfill_campus_map_i18n, noop_reverse),
    ]
