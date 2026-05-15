from django.contrib import admin

from core.admin_mixins import TranslatableUnfoldAdmin, UnfoldAdmin

from .models import (
    AssignmentMaterial,
    ClassAssignment,
    ClassLesson,
    LessonMaterial,
    LessonPlan,
    Room,
    TimeSlot,
)


@admin.register(Room)
class RoomAdmin(TranslatableUnfoldAdmin):
    list_display = ("name", "floor")
    search_fields = ("name", "floor")


@admin.register(TimeSlot)
class TimeSlotAdmin(UnfoldAdmin):
    list_display = ("number", "start_time", "end_time")
    ordering = ("number",)


@admin.register(ClassLesson)
class ClassLessonAdmin(UnfoldAdmin):
    list_display = ("school_class", "weekday", "slot", "subject", "teacher", "room", "is_public")
    list_filter = ("weekday", "school_class", "is_public")
    search_fields = ("school_class__name", "subject__name", "teacher__full_name")


@admin.register(LessonPlan)
class LessonPlanAdmin(TranslatableUnfoldAdmin):
    list_display = ("grade", "subject", "teacher", "title", "date", "is_published")
    list_filter = ("grade", "subject", "is_published")
    search_fields = ("title", "description")


@admin.register(LessonMaterial)
class LessonMaterialAdmin(TranslatableUnfoldAdmin):
    list_display = ("lesson_plan", "title", "created_at")
    search_fields = ("title",)


@admin.register(ClassAssignment)
class ClassAssignmentAdmin(TranslatableUnfoldAdmin):
    list_display = ("grade", "title", "assigned_at", "due_at", "is_published")
    list_filter = ("grade", "is_published")
    search_fields = ("title", "description")


@admin.register(AssignmentMaterial)
class AssignmentMaterialAdmin(TranslatableUnfoldAdmin):
    list_display = ("assignment", "title", "created_at")
    search_fields = ("title",)
