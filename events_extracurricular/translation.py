from modeltranslation.translator import TranslationOptions, translator

from .models import (
    ExtracurricularCategory,
    ExtracurricularEvent,
    ExtracurricularEventGallery,
    ExtracurricularPost,
    ExtracurricularPostGallery,
    ExtracurricularSchedule,
)


class ExtracurricularCategoryTranslationOptions(TranslationOptions):
    fields = ("name",)


class ExtracurricularEventTranslationOptions(TranslationOptions):
    fields = ("title", "description", "place")


class ExtracurricularEventGalleryTranslationOptions(TranslationOptions):
    fields = ("caption",)


class ExtracurricularPostTranslationOptions(TranslationOptions):
    fields = ("title", "body")


class ExtracurricularPostGalleryTranslationOptions(TranslationOptions):
    fields = ("caption",)


class ExtracurricularScheduleTranslationOptions(TranslationOptions):
    fields = ("title", "place")


translator.register(ExtracurricularCategory, ExtracurricularCategoryTranslationOptions)
translator.register(ExtracurricularEvent, ExtracurricularEventTranslationOptions)
translator.register(ExtracurricularEventGallery, ExtracurricularEventGalleryTranslationOptions)
translator.register(ExtracurricularPost, ExtracurricularPostTranslationOptions)
translator.register(ExtracurricularPostGallery, ExtracurricularPostGalleryTranslationOptions)
translator.register(ExtracurricularSchedule, ExtracurricularScheduleTranslationOptions)
