from django.db import migrations


def seed_campus_map(apps, schema_editor):
    CampusMapZone = apps.get_model("site_content", "CampusMapZone")
    CampusMapZonePart = apps.get_model("site_content", "CampusMapZonePart")

    zones = [
        {
            "zone": "under-construction",
            "title": "Under Construction (Not School Territory)",
            "description": (
                "Black building/area is under construction and is not part of the active school territory."
            ),
            "image": "gallery/news-2-720w.jpg",
            "x_pct": "0.00",
            "y_pct": "0.00",
            "width_pct": "53.20",
            "height_pct": "56.60",
            "order": 1,
            "show_in_buttons": True,
            "is_clickable": True,
            "parts": [
                ("No Student Access", "Restricted zone during construction.", ""),
                ("Construction Works", "Area is currently being developed.", ""),
                ("Future Planning", "Reserved for future campus integration.", ""),
            ],
        },
        {
            "zone": "not-school-territory",
            "title": "White Space (Not School Territory)",
            "description": "White space is outside school territory and must stay non-interactive.",
            "image": "gallery/news-2-720w.jpg",
            "x_pct": "92.20",
            "y_pct": "0.00",
            "width_pct": "7.80",
            "height_pct": "100.00",
            "order": 2,
            "show_in_buttons": True,
            "is_clickable": False,
            "parts": [
                ("Outside Campus", "This section is not part of the school area.", ""),
            ],
        },
        {
            "zone": "entrance",
            "title": "Entrance",
            "description": "Small red building at the bottom side used as campus entrance.",
            "image": "gallery/pulatov-school-720w.png",
            "x_pct": "44.80",
            "y_pct": "85.30",
            "width_pct": "8.10",
            "height_pct": "8.50",
            "order": 3,
            "show_in_buttons": True,
            "is_clickable": True,
            "parts": [
                ("Welcome Point", "Entry and reception point for visitors.", ""),
                ("Security Check", "Initial access and monitoring point.", ""),
                ("Access Gate", "Main controlled entry to campus.", ""),
            ],
        },
        {
            "zone": "main-building",
            "title": "Main Building",
            "description": "Large red building containing core academic and support facilities.",
            "image": "infrastructure/pulatov-school-720w.png",
            "x_pct": "41.80",
            "y_pct": "33.70",
            "width_pct": "33.40",
            "height_pct": "21.40",
            "order": 4,
            "show_in_buttons": True,
            "is_clickable": True,
            "parts": [
                ("Medical Center", "Health room and first-aid support.", "gallery/pulotov-720w.jpg"),
                ("Library", "Reading, research and study area.", "gallery/pulatov-2-720w.jpg"),
                ("Cafeteria", "Student and staff meal area.", "gallery/news-2-720w.jpg"),
                ("Computer Center", "ICT labs and digital classes.", "infrastructure/pulatov-school-720w.png"),
            ],
        },
        {
            "zone": "yard",
            "title": "Yard",
            "description": "Open area directly under the main building.",
            "image": "gallery/pulatov-2-720w.jpg",
            "x_pct": "40.80",
            "y_pct": "55.30",
            "width_pct": "37.30",
            "height_pct": "15.70",
            "order": 5,
            "show_in_buttons": True,
            "is_clickable": True,
            "parts": [
                ("Assembly Area", "Morning and event gathering space.", ""),
                ("Student Flow Zone", "Main circulation corridor outside classes.", ""),
                ("Outdoor Activity", "Flexible open-air activities.", ""),
            ],
        },
        {
            "zone": "trees-garden",
            "title": "Trees Garden",
            "description": "Garden area with rows of trees above the main building.",
            "image": "gallery/pulatov-2-720w.jpg",
            "x_pct": "43.00",
            "y_pct": "7.80",
            "width_pct": "29.30",
            "height_pct": "21.20",
            "order": 6,
            "show_in_buttons": True,
            "is_clickable": True,
            "parts": [
                ("Tree Rows", "Organized green plantation.", ""),
                ("Garden Paths", "Walkways between planted sections.", ""),
                ("Outdoor Relaxation", "Quiet area for short breaks.", ""),
            ],
        },
        {
            "zone": "football-stadium",
            "title": "Football Stadium",
            "description": "Football field located on the right side of the main building.",
            "image": "gallery/pulotov-720w.jpg",
            "x_pct": "69.90",
            "y_pct": "10.90",
            "width_pct": "21.30",
            "height_pct": "50.60",
            "order": 7,
            "show_in_buttons": True,
            "is_clickable": True,
            "parts": [
                ("Training Field", "Daily football training sessions.", ""),
                ("PE Activity", "Physical education classes.", ""),
                ("Competition Matches", "School sports events and matches.", ""),
            ],
        },
    ]

    for zone_payload in zones:
        parts = zone_payload.pop("parts", [])
        zone_obj, _ = CampusMapZone.objects.update_or_create(
            zone=zone_payload["zone"],
            defaults=zone_payload,
        )

        existing_parts = {p.title: p for p in zone_obj.parts.all()}
        seen_titles = set()
        for index, (title, description, image) in enumerate(parts, start=1):
            seen_titles.add(title)
            part_defaults = {
                "order": index,
                "description": description,
                "is_public": True,
            }
            if image:
                part_defaults["image"] = image
            part_obj = existing_parts.get(title)
            if part_obj:
                for field, value in part_defaults.items():
                    setattr(part_obj, field, value)
                part_obj.save(update_fields=list(part_defaults.keys()))
            else:
                CampusMapZonePart.objects.create(
                    zone=zone_obj,
                    title=title,
                    **part_defaults,
                )

        for title, part in existing_parts.items():
            if title not in seen_titles:
                part.delete()


def unseed_campus_map(apps, schema_editor):
    CampusMapZone = apps.get_model("site_content", "CampusMapZone")
    CampusMapZonePart = apps.get_model("site_content", "CampusMapZonePart")
    CampusMapZonePart.objects.all().delete()
    CampusMapZone.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("site_content", "0002_campusmapzone_campusmapzonepart"),
    ]

    operations = [
        migrations.RunPython(seed_campus_map, unseed_campus_map),
    ]
