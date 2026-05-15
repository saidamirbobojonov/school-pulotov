from django.db import migrations


def add_future_gym_zone(apps, schema_editor):
    CampusMapZone = apps.get_model("site_content", "CampusMapZone")
    if CampusMapZone.objects.filter(zone="future-gym").exists():
        return
    max_order = (
        CampusMapZone.objects.order_by("-order").values_list("order", flat=True).first() or 0
    )
    CampusMapZone.objects.create(
        zone="future-gym",
        title="Future Building (Gym)",
        description="",
        x_pct=82,
        y_pct=78,
        width_pct=12,
        height_pct=12,
        order=max_order + 1,
        is_public=True,
        show_in_buttons=True,
        is_clickable=True,
    )


def remove_future_gym_zone(apps, schema_editor):
    CampusMapZone = apps.get_model("site_content", "CampusMapZone")
    CampusMapZone.objects.filter(zone="future-gym").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("site_content", "0010_update_gallery_categories"),
    ]

    operations = [
        migrations.RunPython(add_future_gym_zone, remove_future_gym_zone),
    ]
