from django.contrib import admin

from core.admin_mixins import TranslatableUnfoldAdmin
from modeltranslation.admin import TranslationTabularInline

from .models import NewsGallery, NewsPost


class NewsGalleryInline(TranslationTabularInline):
    model = NewsGallery
    extra = 0


@admin.register(NewsPost)
class NewsPostAdmin(TranslatableUnfoldAdmin):
    list_display = ("title", "category", "published_at", "views", "is_published")
    list_filter = ("category",)
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}
    inlines = (NewsGalleryInline,)


@admin.register(NewsGallery)
class NewsGalleryAdmin(TranslatableUnfoldAdmin):
    list_display = ("news", "caption", "created_at")
    list_filter = ("news",)
