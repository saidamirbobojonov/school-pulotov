from django.contrib import admin

from core.admin_mixins import TranslatableUnfoldAdmin
from modeltranslation.admin import TranslationTabularInline

from .models import (
    ExtracurricularCategory,
    ExtracurricularEvent,
    ExtracurricularEventGallery,
    ExtracurricularPost,
    ExtracurricularPostGallery,
    ExtracurricularSchedule,
)


class ExtracurricularEventGalleryInline(TranslationTabularInline):
    model = ExtracurricularEventGallery
    extra = 0


class ExtracurricularPostGalleryInline(TranslationTabularInline):
    model = ExtracurricularPostGallery
    extra = 0


@admin.register(ExtracurricularCategory)
class ExtracurricularCategoryAdmin(TranslatableUnfoldAdmin):
    list_display = ("name", "order")
    ordering = ("order", "name")


@admin.register(ExtracurricularEvent)
class ExtracurricularEventAdmin(TranslatableUnfoldAdmin):
    list_display = ("title", "category", "school_class", "start_at", "place", "is_public")
    list_filter = ("category", "school_class", "is_public")
    search_fields = ("title", "description", "place")
    inlines = (ExtracurricularEventGalleryInline,)


@admin.register(ExtracurricularEventGallery)
class ExtracurricularEventGalleryAdmin(TranslatableUnfoldAdmin):
    list_display = ("event", "caption", "created_at")
    list_filter = ("event",)


@admin.register(ExtracurricularPost)
class ExtracurricularPostAdmin(TranslatableUnfoldAdmin):
    list_display = ("title", "event", "published_at", "views", "is_approved")
    list_filter = ("is_approved", "event")
    search_fields = ("title", "body")
    inlines = (ExtracurricularPostGalleryInline,)


@admin.register(ExtracurricularPostGallery)
class ExtracurricularPostGalleryAdmin(TranslatableUnfoldAdmin):
    list_display = ("post", "caption", "created_at")
    list_filter = ("post",)


@admin.register(ExtracurricularSchedule)
class ExtracurricularScheduleAdmin(TranslatableUnfoldAdmin):
    list_display = ("title", "grade", "when", "place", "is_active")
    list_filter = ("grade", "is_active")
    search_fields = ("title", "place")
