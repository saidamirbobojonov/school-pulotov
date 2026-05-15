from django.contrib import admin

from core.admin_mixins import TranslatableUnfoldAdmin, UnfoldAdmin

from .models import ConstructionGalleryImage, ConstructionPost, PerspectiveOverview, PerspectiveSection


class ConstructionGalleryInline(admin.TabularInline):
    model = ConstructionGalleryImage
    extra = 0
    fields = ("image", "caption", "order")


@admin.register(ConstructionPost)
class ConstructionPostAdmin(TranslatableUnfoldAdmin):
    list_display = ("title", "slug", "created_at")
    search_fields = ("title", "slug", "text")
    ordering = ("-created_at", "-id")
    inlines = (ConstructionGalleryInline,)


@admin.register(PerspectiveOverview)
class PerspectiveOverviewAdmin(TranslatableUnfoldAdmin):
    pass


@admin.register(PerspectiveSection)
class PerspectiveSectionAdmin(TranslatableUnfoldAdmin):
    list_display = ("section_type", "title", "updated_at")
    list_filter = ("section_type",)
    search_fields = ("title", "text")
    ordering = ("section_type", "id")
