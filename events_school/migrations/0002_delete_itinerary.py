from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("events_school", "0001_initial"),
    ]

    operations = [
        migrations.DeleteModel(
            name="SchoolEventItineraryItem",
        ),
    ]
