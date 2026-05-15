from django.db import migrations


def backfill_part_images(apps, schema_editor):
    CampusMapZone = apps.get_model("site_content", "CampusMapZone")
    CampusMapZonePart = apps.get_model("site_content", "CampusMapZonePart")

    fallback_by_zone = {
        "under-construction": "gallery/news-2-720w.jpg",
        "not-school-territory": "gallery/news-2-720w.jpg",
        "entrance": "gallery/pulatov-school-720w.png",
        "yard": "gallery/pulatov-2-720w.jpg",
        "trees-garden": "gallery/pulatov-2-720w.jpg",
        "football-stadium": "gallery/pulotov-720w.jpg",
    }

    zone_image_map = {}
    for zone in CampusMapZone.objects.all():
        if zone.image:
            zone_image_map[zone.zone] = zone.image.name

    for part in CampusMapZonePart.objects.select_related("zone").all():
        if part.image:
            continue
        zone_key = part.zone.zone
        image_name = zone_image_map.get(zone_key) or fallback_by_zone.get(zone_key)
        if image_name:
            part.image = image_name
            part.save(update_fields=["image"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("site_content", "0004_backfill_campus_map_i18n"),
    ]

    operations = [
        migrations.RunPython(backfill_part_images, noop_reverse),
    ]
