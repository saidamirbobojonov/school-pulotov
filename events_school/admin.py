from django.contrib import admin

from core.admin_mixins import TranslatableUnfoldAdmin
from modeltranslation.admin import TranslationTabularInline

from .models import (
    SchoolEvent,
    SchoolEventCategory,
    SchoolEventGallery,
    SchoolEventPost,
    SchoolEventPostGallery,
)


class SchoolEventGalleryInline(TranslationTabularInline):
    model = SchoolEventGallery
    extra = 0


class SchoolEventPostGalleryInline(TranslationTabularInline):
    model = SchoolEventPostGallery
    extra = 0


@admin.register(SchoolEventCategory)
class SchoolEventCategoryAdmin(TranslatableUnfoldAdmin):
    list_display = ("name", "order")
    ordering = ("order", "name")


@admin.register(SchoolEvent)
class SchoolEventAdmin(TranslatableUnfoldAdmin):
    list_display = ("title", "category", "school_class", "start_at", "place", "is_public")
    list_filter = ("category", "school_class", "is_public")
    search_fields = ("title", "description", "place")
    inlines = (SchoolEventGalleryInline,)


@admin.register(SchoolEventGallery)
class SchoolEventGalleryAdmin(TranslatableUnfoldAdmin):
    list_display = ("event", "caption", "created_at")
    list_filter = ("event",)


@admin.register(SchoolEventPost)
class SchoolEventPostAdmin(TranslatableUnfoldAdmin):
    list_display = ("title", "event", "published_at", "views", "is_approved")
    list_filter = ("is_approved", "event")
    search_fields = ("title", "body")
    inlines = (SchoolEventPostGalleryInline,)


@admin.register(SchoolEventPostGallery)
class SchoolEventPostGalleryAdmin(TranslatableUnfoldAdmin):
    list_display = ("post", "caption", "created_at")
    list_filter = ("post",)
