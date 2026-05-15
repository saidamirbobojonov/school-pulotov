from django.db import migrations, models


def copy_grade_from_class(apps, schema_editor):
    LessonPlan = apps.get_model("academics", "LessonPlan")
    ClassAssignment = apps.get_model("academics", "ClassAssignment")

    for plan in LessonPlan.objects.select_related("school_class").all():
        grade = getattr(plan.school_class, "grade", None) if getattr(plan, "school_class_id", None) else None
        plan.grade = grade or 1
        plan.save(update_fields=["grade"])

    for assignment in ClassAssignment.objects.select_related("school_class").all():
        grade = getattr(assignment.school_class, "grade", None) if getattr(assignment, "school_class_id", None) else None
        assignment.grade = grade or 1
        assignment.save(update_fields=["grade"])


class Migration(migrations.Migration):
    dependencies = [
        ("academics", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="lessonplan",
            name="grade",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5"), (6, "6"), (7, "7"), (8, "8"), (9, "9"), (10, "10"), (11, "11")],
                verbose_name="Класс (1–11)",
            ),
        ),
        migrations.AddField(
            model_name="classassignment",
            name="grade",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5"), (6, "6"), (7, "7"), (8, "8"), (9, "9"), (10, "10"), (11, "11")],
                verbose_name="Класс (1–11)",
            ),
        ),
        migrations.RunPython(copy_grade_from_class, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="lessonplan",
            name="school_class",
        ),
        migrations.RemoveField(
            model_name="classassignment",
            name="school_class",
        ),
        migrations.AlterField(
            model_name="lessonplan",
            name="grade",
            field=models.PositiveSmallIntegerField(
                choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5"), (6, "6"), (7, "7"), (8, "8"), (9, "9"), (10, "10"), (11, "11")],
                default=1,
                verbose_name="Класс (1–11)",
            ),
        ),
        migrations.AlterField(
            model_name="classassignment",
            name="grade",
            field=models.PositiveSmallIntegerField(
                choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5"), (6, "6"), (7, "7"), (8, "8"), (9, "9"), (10, "10"), (11, "11")],
                default=1,
                verbose_name="Класс (1–11)",
            ),
        ),
    ]
