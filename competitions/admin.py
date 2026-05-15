from django.contrib import admin

from core.admin_mixins import TranslatableUnfoldAdmin

from .models import CompetitionResult, CompetitionType, SchoolHonor


@admin.register(CompetitionType)
class CompetitionTypeAdmin(TranslatableUnfoldAdmin):
    list_display = ("name", "order")
    ordering = ("order", "name")
    search_fields = ("name",)


@admin.register(CompetitionResult)
class CompetitionResultAdmin(TranslatableUnfoldAdmin):
    list_display = ("title", "year", "level", "student", "subject", "competition_type")
    list_filter = ("year", "level", "competition_type", "subject")
    search_fields = ("title", "student__full_name")


@admin.register(SchoolHonor)
class SchoolHonorAdmin(TranslatableUnfoldAdmin):
    list_display = ("title", "year", "order", "is_public")
    list_filter = ("is_public", "year")
    ordering = ("order", "-year", "-created_at", "-id")
    search_fields = ("title", "description")
