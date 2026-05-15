from modeltranslation.translator import TranslationOptions, translator

from .models import (
    SchoolEvent,
    SchoolEventCategory,
    SchoolEventGallery,
    SchoolEventPost,
    SchoolEventPostGallery,
)


class SchoolEventCategoryTranslationOptions(TranslationOptions):
    fields = ("name",)


class SchoolEventTranslationOptions(TranslationOptions):
    fields = ("title", "description", "place")


class SchoolEventGalleryTranslationOptions(TranslationOptions):
    fields = ("caption",)


class SchoolEventPostTranslationOptions(TranslationOptions):
    fields = ("title", "body")


class SchoolEventPostGalleryTranslationOptions(TranslationOptions):
    fields = ("caption",)

translator.register(SchoolEventCategory, SchoolEventCategoryTranslationOptions)
translator.register(SchoolEvent, SchoolEventTranslationOptions)
translator.register(SchoolEventGallery, SchoolEventGalleryTranslationOptions)
translator.register(SchoolEventPost, SchoolEventPostTranslationOptions)
translator.register(SchoolEventPostGallery, SchoolEventPostGalleryTranslationOptions)
