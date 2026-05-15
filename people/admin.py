from django.contrib import admin
from django.utils.html import format_html

from core.admin_mixins import TranslatableUnfoldAdmin, UnfoldAdmin
from modeltranslation.admin import TranslationTabularInline

from academics.models import ClassLesson
from .models import GraduateDestination, GraduateStudyRecord, SchoolClass, Staff, Student, Subject

try:
    from unfold.admin import TabularInline as UnfoldTabularInline
except Exception:  # pragma: no cover
    from django.contrib.admin import TabularInline as UnfoldTabularInline


class ClassLessonInline(UnfoldTabularInline):
    model = ClassLesson
    extra = 0
    fields = ("weekday", "slot", "subject", "teacher", "room", "is_public")


@admin.register(SchoolClass)
class SchoolClassAdmin(UnfoldAdmin):
    list_display = ("grade", "name", "is_active")
    list_filter = ("grade", "is_active")
    search_fields = ("name",)
    inlines = (ClassLessonInline,)


@admin.register(Subject)
class SubjectAdmin(TranslatableUnfoldAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Staff)
class StaffAdmin(TranslatableUnfoldAdmin):
    list_display = ("full_name", "photo", "role", "order")
    list_editable = ("photo", "role", "order")
    list_filter = ("role",)
    search_fields = ("full_name",)
    ordering = ("order", "role", "full_name")


@admin.register(Student)
class StudentAdmin(TranslatableUnfoldAdmin):
    list_display = ("full_name", "school_class")
    list_filter = ("school_class",)
    search_fields = ("full_name",)


class GraduateStudyRecordInline(TranslationTabularInline):
    model = GraduateStudyRecord
    extra = 0
    show_change_link = True
    fields = (
        "full_name",
        "photo_1",
        "photo_2",
        "graduation_year",
        "university_name",
        "program",
        "degree",
        "start_year",
        "is_public",
        "order",
    )


@admin.register(GraduateDestination)
class GraduateDestinationAdmin(TranslatableUnfoldAdmin):
    list_display = ("city", "country", "coords", "graduates_count", "is_public", "updated_at")
    list_filter = ("is_public", "country")
    search_fields = ("city", "country", "title", "description")
    ordering = ("country", "city", "id")
    inlines = (GraduateStudyRecordInline,)
    readonly_fields = ("image_preview", "created_at", "updated_at")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("city", "country"),
                    ("latitude", "longitude"),
                    ("title",),
                    ("description",),
                    ("image", "image_preview"),
                    ("assistant_url",),
                    ("is_public",),
                    ("created_at", "updated_at"),
                )
            },
        ),
    )

    @admin.display(description="Координаты")
    def coords(self, obj: GraduateDestination) -> str:
        return f"{obj.latitude:.4f}, {obj.longitude:.4f}"

    @admin.display(description="Выпускников")
    def graduates_count(self, obj: GraduateDestination) -> int:
        return obj.graduates.count()

    @admin.display(description="Превью")
    def image_preview(self, obj: GraduateDestination) -> str:
        if not obj.image:
            return "—"
        return format_html(
            '<img src="{}" style="max-height:120px;max-width:220px;border-radius:12px;object-fit:cover;" />',
            obj.image.url,
        )


@admin.register(GraduateStudyRecord)
class GraduateStudyRecordAdmin(TranslatableUnfoldAdmin):
    list_display = ("full_name", "graduation_year", "university_name", "destination", "is_public", "order")
    list_filter = ("is_public", "graduation_year", "destination__country")
    search_fields = ("full_name", "university_name", "program", "degree", "destination__city", "destination__country")
    ordering = ("destination__country", "destination__city", "order", "id")
    list_editable = ("is_public", "order")
    autocomplete_fields = ("destination",)
