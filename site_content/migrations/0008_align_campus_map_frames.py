from django.db import migrations


def align_campus_map_frames(apps, schema_editor):
    CampusMapZone = apps.get_model("site_content", "CampusMapZone")

    # Coordinates are aligned to the updated school plan and separated by grey roads.
    # Values are percentages relative to the full map image.
    frame_map = {
        "trees-garden": {"x_pct": "56.80", "y_pct": "5.80", "width_pct": "24.40", "height_pct": "20.70"},
        "main-building": {"x_pct": "56.80", "y_pct": "28.20", "width_pct": "24.60", "height_pct": "22.40"},
        "football-stadium": {"x_pct": "82.70", "y_pct": "18.20", "width_pct": "11.60", "height_pct": "34.80"},
        "yard": {"x_pct": "56.70", "y_pct": "53.00", "width_pct": "30.40", "height_pct": "39.20"},
        "under-construction": {"x_pct": "30.30", "y_pct": "53.00", "width_pct": "24.30", "height_pct": "31.20"},
        "entrance": {"x_pct": "43.90", "y_pct": "89.90", "width_pct": "10.70", "height_pct": "9.20"},
        "future-buildings": {"x_pct": "0.80", "y_pct": "54.20", "width_pct": "28.20", "height_pct": "34.80"},
        "not-school-territory": {"x_pct": "94.50", "y_pct": "0.00", "width_pct": "5.50", "height_pct": "100.00"},
    }

    defaults = {
        "under-construction": {
            "title": "Under Construction",
            "description": "Black building is under construction and currently restricted.",
            "order": 1,
            "is_public": True,
            "show_in_buttons": True,
            "is_clickable": True,
        },
        "future-buildings": {
            "title": "Future Buildings",
            "description": "Reserved school area for future building expansion.",
            "order": 2,
            "is_public": True,
            "show_in_buttons": True,
            "is_clickable": True,
        },
        "main-building": {
            "title": "Main Building",
            "description": "Large red building with core academic facilities.",
            "order": 3,
            "is_public": True,
            "show_in_buttons": True,
            "is_clickable": True,
        },
        "trees-garden": {
            "title": "Trees Garden",
            "description": "Garden area above the main building.",
            "order": 4,
            "is_public": True,
            "show_in_buttons": True,
            "is_clickable": True,
        },
        "football-stadium": {
            "title": "Football Stadium",
            "description": "Football field on the right side of the campus.",
            "order": 5,
            "is_public": True,
            "show_in_buttons": True,
            "is_clickable": True,
        },
        "yard": {
            "title": "Yard",
            "description": "Open yard area below the main building.",
            "order": 6,
            "is_public": True,
            "show_in_buttons": True,
            "is_clickable": True,
        },
        "entrance": {
            "title": "Entrance",
            "description": "Small red entrance building.",
            "order": 7,
            "is_public": True,
            "show_in_buttons": True,
            "is_clickable": True,
        },
        "not-school-territory": {
            "title": "Not School Territory",
            "description": "White-space outside school territory. Hidden on interactive map.",
            "order": 8,
            "is_public": True,
            "show_in_buttons": False,
            "is_clickable": False,
        },
    }

    for zone_key, values in defaults.items():
        zone_obj, _ = CampusMapZone.objects.get_or_create(
            zone=zone_key,
            defaults={**values, **frame_map[zone_key]},
        )
        for field, value in {**frame_map[zone_key], **values}.items():
            setattr(zone_obj, field, value)
        zone_obj.save()


def reverse_align_campus_map_frames(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("site_content", "0007_alter_campusmapzone_zone_and_more"),
    ]

    operations = [
        migrations.RunPython(align_campus_map_frames, reverse_align_campus_map_frames),
    ]
