from django.contrib import admin

from core.admin_mixins import TranslatableUnfoldAdmin, UnfoldAdmin

from .models import AdmissionApplication, AdmissionApplicationDocument, ContactMessage, ContactPage


@admin.register(ContactPage)
class ContactPageAdmin(TranslatableUnfoldAdmin):
    pass


@admin.register(ContactMessage)
class ContactMessageAdmin(UnfoldAdmin):
    list_display = ("created_at", "name", "phone", "subject", "is_read")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "phone", "subject", "message")


class AdmissionApplicationDocumentInline(admin.TabularInline):
    model = AdmissionApplicationDocument
    extra = 0
    fields = ("file", "original_name", "created_at")
    readonly_fields = ("created_at",)


@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(UnfoldAdmin):
    list_display = ("created_at", "student_name", "grade", "parent_name", "phone", "status")
    list_filter = ("status", "grade", "created_at")
    search_fields = ("student_name", "parent_name", "phone", "email", "note")
    inlines = (AdmissionApplicationDocumentInline,)
