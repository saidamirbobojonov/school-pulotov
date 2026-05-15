from django.contrib import admin

from core.admin_mixins import TranslatableUnfoldAdmin

from .models import MenuItem


@admin.register(MenuItem)
class MenuItemAdmin(TranslatableUnfoldAdmin):
    list_display = ("title", "menu_type", "order", "parent", "is_active", "show_in_footer", "route_name", "custom_url")
    list_filter = ("menu_type", "is_active", "show_in_footer")
    ordering = ("order", "id")
    search_fields = ("title", "route_name", "custom_url")
