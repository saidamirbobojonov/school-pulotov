from modeltranslation.translator import TranslationOptions, translator

from .models import ConstructionGalleryImage, ConstructionPost, PerspectiveOverview, PerspectiveSection


class PerspectiveOverviewTranslationOptions(TranslationOptions):
    fields = ("title", "text")


class ConstructionPostTranslationOptions(TranslationOptions):
    fields = ("title", "text")


class ConstructionGalleryImageTranslationOptions(TranslationOptions):
    fields = ("caption",)


class PerspectiveSectionTranslationOptions(TranslationOptions):
    fields = ("title", "text")


translator.register(PerspectiveOverview, PerspectiveOverviewTranslationOptions)
translator.register(ConstructionPost, ConstructionPostTranslationOptions)
translator.register(ConstructionGalleryImage, ConstructionGalleryImageTranslationOptions)
translator.register(PerspectiveSection, PerspectiveSectionTranslationOptions)
