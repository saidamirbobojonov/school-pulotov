from modeltranslation.translator import TranslationOptions, translator

from .models import (
    CampusMapZone,
    CampusMapZonePart,
    AdmissionImportantDate,
    AdmissionStep,
    AdmissionsPage,
    Announcement,
    EducationType,
    FAQItem,
    GalleryAlbum,
    GalleryImage,
    Hero,
    ParentsCommitteeFocusArea,
    ParentsCommitteeMeeting,
    ParentsCommitteeMember,
    ParentsCommitteePage,
    MethodicalMaterial,
    StudentsCommunityMember,
    StudentsCommunityPage,
    TeachersCommitteeFocusArea,
    TeachersCommitteeMeeting,
    TeachersCommitteeMember,
    TeachersCommitteePage,
    SchoolContent,
    SchoolName,
    Slogan,
)


class SchoolNameTranslationOptions(TranslationOptions):
    fields = ("name",)


class SchoolContentTranslationOptions(TranslationOptions):
    fields = ("big_info_title", "big_info_text", "history_title", "history_text")


class HeroTranslationOptions(TranslationOptions):
    fields = ("title", "text")


class AnnouncementTranslationOptions(TranslationOptions):
    fields = ("title", "body")


translator.register(SchoolName, SchoolNameTranslationOptions)
translator.register(SchoolContent, SchoolContentTranslationOptions)
translator.register(Hero, HeroTranslationOptions)
translator.register(Announcement, AnnouncementTranslationOptions)


class GalleryImageTranslationOptions(TranslationOptions):
    fields = ("caption",)


class FAQItemTranslationOptions(TranslationOptions):
    fields = ("question", "answer")


class GalleryAlbumTranslationOptions(TranslationOptions):
    fields = ("title",)


translator.register(GalleryAlbum, GalleryAlbumTranslationOptions)
translator.register(GalleryImage, GalleryImageTranslationOptions)
translator.register(FAQItem, FAQItemTranslationOptions)


class SloganTranslationOptions(TranslationOptions):
    fields = ("title", "text")

translator.register(Slogan, SloganTranslationOptions)


class AdmissionsPageTranslationOptions(TranslationOptions):
    fields = (
        "hero_title",
        "hero_text",
        "process_title",
        "process_text",
        "form_title",
        "dates_title",
        "questions_title",
        "questions_text",
    )


class AdmissionStepTranslationOptions(TranslationOptions):
    fields = ("title", "description")


class AdmissionImportantDateTranslationOptions(TranslationOptions):
    fields = ("label", "date_text")


translator.register(AdmissionsPage, AdmissionsPageTranslationOptions)
translator.register(AdmissionStep, AdmissionStepTranslationOptions)
translator.register(AdmissionImportantDate, AdmissionImportantDateTranslationOptions)


class MethodicalMaterialTranslationOptions(TranslationOptions):
    fields = ("title",)


translator.register(MethodicalMaterial, MethodicalMaterialTranslationOptions)


class EducationTypeTranslationOptions(TranslationOptions):
    fields = ("title", "text")


translator.register(EducationType, EducationTypeTranslationOptions)


class ParentsCommitteePageTranslationOptions(TranslationOptions):
    fields = ("mission_title", "mission_text", "mission_text_2", "members_intro", "meetings_intro")


class ParentsCommitteeFocusAreaTranslationOptions(TranslationOptions):
    fields = ("title",)


class ParentsCommitteeMemberTranslationOptions(TranslationOptions):
    fields = ("role", "full_name")


class ParentsCommitteeMeetingTranslationOptions(TranslationOptions):
    fields = ("location", "agenda_topic")


translator.register(ParentsCommitteePage, ParentsCommitteePageTranslationOptions)
translator.register(ParentsCommitteeFocusArea, ParentsCommitteeFocusAreaTranslationOptions)
translator.register(ParentsCommitteeMember, ParentsCommitteeMemberTranslationOptions)
translator.register(ParentsCommitteeMeeting, ParentsCommitteeMeetingTranslationOptions)


class TeachersCommitteePageTranslationOptions(TranslationOptions):
    fields = ("mission_title", "mission_text", "mission_text_2", "members_intro", "meetings_intro")


class TeachersCommitteeFocusAreaTranslationOptions(TranslationOptions):
    fields = ("title",)


class TeachersCommitteeMemberTranslationOptions(TranslationOptions):
    fields = ("role_title",)


class TeachersCommitteeMeetingTranslationOptions(TranslationOptions):
    fields = ("location", "agenda_topic")


translator.register(TeachersCommitteePage, TeachersCommitteePageTranslationOptions)
translator.register(TeachersCommitteeFocusArea, TeachersCommitteeFocusAreaTranslationOptions)
translator.register(TeachersCommitteeMember, TeachersCommitteeMemberTranslationOptions)
translator.register(TeachersCommitteeMeeting, TeachersCommitteeMeetingTranslationOptions)


class StudentsCommunityPageTranslationOptions(TranslationOptions):
    fields = ("mission_title", "mission_text", "mission_text_2", "members_intro")


class StudentsCommunityMemberTranslationOptions(TranslationOptions):
    fields = ("role_title",)


translator.register(StudentsCommunityPage, StudentsCommunityPageTranslationOptions)
translator.register(StudentsCommunityMember, StudentsCommunityMemberTranslationOptions)


class CampusMapZoneTranslationOptions(TranslationOptions):
    fields = ("title", "description")


class CampusMapZonePartTranslationOptions(TranslationOptions):
    fields = ("title", "description")


translator.register(CampusMapZone, CampusMapZoneTranslationOptions)
translator.register(CampusMapZonePart, CampusMapZonePartTranslationOptions)
