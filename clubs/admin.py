from django.contrib import admin

from core.admin_mixins import TranslatableUnfoldAdmin
from modeltranslation.admin import TranslationTabularInline

from .models import Club, ClubGallery


class ClubGalleryInline(TranslationTabularInline):
    model = ClubGallery
    extra = 0


@admin.register(Club)
class ClubAdmin(TranslatableUnfoldAdmin):
    list_display = ("name", "leader", "is_public")
    list_filter = ("is_public",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = (ClubGalleryInline,)


@admin.register(ClubGallery)
class ClubGalleryAdmin(TranslatableUnfoldAdmin):
    list_display = ("club", "caption", "created_at")
    list_filter = ("club",)
