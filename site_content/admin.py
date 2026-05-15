from django.contrib import admin

from core.admin_mixins import TranslatableUnfoldAdmin, UnfoldAdmin
from modeltranslation.admin import TranslationTabularInline

from .models import (
    CampusMapZone,
    CampusMapZonePart,
    AdmissionImportantDate,
    AdmissionStep,
    Announcement,
    AdmissionsPage,
    FAQItem,
    GalleryAlbum,
    GalleryImage,
    Hero,
    ParentsCommitteeFocusArea,
    ParentsCommitteeMeeting,
    ParentsCommitteeMember,
    ParentsCommitteePage,
    MethodicalMaterial,
    EducationType,
    StudentsCommunityMember,
    StudentsCommunityPage,
    TeachersCommitteeFocusArea,
    TeachersCommitteeMeeting,
    TeachersCommitteeMember,
    TeachersCommitteePage,
    SchoolContent,
    SchoolName,
    SocialNetwork,
    Slogan,
)


@admin.register(SchoolName)
class SchoolNameAdmin(TranslatableUnfoldAdmin):
    pass


@admin.register(SchoolContent)
class SchoolContentAdmin(TranslatableUnfoldAdmin):
    pass


@admin.register(SocialNetwork)
class SocialNetworkAdmin(UnfoldAdmin):
    list_display = ("link", "order")
    ordering = ("order", "created_at")


@admin.register(Hero)
class HeroAdmin(TranslatableUnfoldAdmin):
    list_display = ("title", "menu_item", "order")
    list_filter = ("menu_item",)
    ordering = ("order", "id")


@admin.register(Announcement)
class AnnouncementAdmin(TranslatableUnfoldAdmin):
    list_display = ("title", "start_at", "end_at", "is_active")
    list_filter = ("start_at",)


@admin.register(GalleryImage)
class GalleryImageAdmin(TranslatableUnfoldAdmin):
    list_display = ("caption", "album", "order", "is_public", "created_at")
    list_filter = ("album", "is_public")
    ordering = ("album__order", "order", "-created_at", "-id")
    search_fields = ("caption", "album__title")


class GalleryImageInline(TranslationTabularInline):
    model = GalleryImage
    extra = 0
    fields = ("image", "caption", "order", "is_public")


@admin.register(GalleryAlbum)
class GalleryAlbumAdmin(TranslatableUnfoldAdmin):
    list_display = ("title", "slug", "order", "is_public", "created_at")
    list_filter = ("is_public",)
    search_fields = ("title", "slug")
    ordering = ("order", "id")
    inlines = (GalleryImageInline,)


@admin.register(FAQItem)
class FAQItemAdmin(TranslatableUnfoldAdmin):
    list_display = ("question", "order", "is_active", "created_at")
    list_filter = ("is_active",)
    ordering = ("order", "id")
    search_fields = ("question", "answer")


@admin.register(Slogan)
class SloganAdmin(TranslatableUnfoldAdmin):
    list_display = ("title", "order", "is_active", "created_at")
    list_filter = ("is_active",)
    ordering = ("order", "id")
    search_fields = ("title", "text")


class AdmissionStepInline(TranslationTabularInline):
    model = AdmissionStep
    extra = 0


class AdmissionImportantDateInline(TranslationTabularInline):
    model = AdmissionImportantDate
    extra = 0


@admin.register(AdmissionsPage)
class AdmissionsPageAdmin(TranslatableUnfoldAdmin):
    inlines = (AdmissionStepInline, AdmissionImportantDateInline)


@admin.register(MethodicalMaterial)
class MethodicalMaterialAdmin(UnfoldAdmin):
    list_display = ("title", "created_at")
    search_fields = ("title",)
    ordering = ("-created_at", "-id")


@admin.register(EducationType)
class EducationTypeAdmin(TranslatableUnfoldAdmin):
    list_display = ("title", "order", "is_active")
    list_filter = ("is_active",)
    ordering = ("order", "id")
    search_fields = ("title", "text")


class ParentsCommitteeFocusAreaInline(TranslationTabularInline):
    model = ParentsCommitteeFocusArea
    extra = 0


class ParentsCommitteeMemberInline(TranslationTabularInline):
    model = ParentsCommitteeMember
    extra = 0


class ParentsCommitteeMeetingInline(TranslationTabularInline):
    model = ParentsCommitteeMeeting
    extra = 0


@admin.register(ParentsCommitteePage)
class ParentsCommitteePageAdmin(TranslatableUnfoldAdmin):
    inlines = (ParentsCommitteeFocusAreaInline, ParentsCommitteeMemberInline, ParentsCommitteeMeetingInline)


class TeachersCommitteeFocusAreaInline(TranslationTabularInline):
    model = TeachersCommitteeFocusArea
    extra = 0


class TeachersCommitteeMemberInline(TranslationTabularInline):
    model = TeachersCommitteeMember
    extra = 0
    autocomplete_fields = ("staff",)


class TeachersCommitteeMeetingInline(TranslationTabularInline):
    model = TeachersCommitteeMeeting
    extra = 0


@admin.register(TeachersCommitteePage)
class TeachersCommitteePageAdmin(TranslatableUnfoldAdmin):
    inlines = (TeachersCommitteeFocusAreaInline, TeachersCommitteeMemberInline, TeachersCommitteeMeetingInline)


class StudentsCommunityMemberInline(TranslationTabularInline):
    model = StudentsCommunityMember
    extra = 0
    autocomplete_fields = ("student",)


@admin.register(StudentsCommunityPage)
class StudentsCommunityPageAdmin(TranslatableUnfoldAdmin):
    inlines = (StudentsCommunityMemberInline,)


class CampusMapZonePartInline(TranslationTabularInline):
    model = CampusMapZonePart
    extra = 0
    fields = ("order", "title", "description", "image", "is_public")


@admin.register(CampusMapZone)
class CampusMapZoneAdmin(TranslatableUnfoldAdmin):
    list_display = (
        "title",
        "zone",
        "order",
        "x_pct",
        "y_pct",
        "width_pct",
        "height_pct",
        "is_public",
        "is_clickable",
        "show_in_buttons",
    )
    list_filter = ("zone", "is_public", "is_clickable", "show_in_buttons")
    ordering = ("order", "id")
    search_fields = ("title", "description")
    fieldsets = (
        (
            "Site Category: Map Zone",
            {
                "fields": (
                    "zone",
                    "title",
                    "description",
                    "image",
                    "order",
                    "is_public",
                    "show_in_buttons",
                    "is_clickable",
                ),
            },
        ),
        (
            "Map Frame Coordinates",
            {
                "fields": ("x_pct", "y_pct", "width_pct", "height_pct"),
                "description": "Use percentage values to place the clickable frame on the campus image.",
            },
        ),
    )
    inlines = (CampusMapZonePartInline,)
