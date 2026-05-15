from modeltranslation.translator import TranslationOptions, translator

from .models import Club, ClubGallery




class ClubTranslationOptions(TranslationOptions):
    fields = ("name", "description", "schedule_text")


class ClubGalleryTranslationOptions(TranslationOptions):
    fields = ("caption",)


translator.register(Club, ClubTranslationOptions)
translator.register(ClubGallery, ClubGalleryTranslationOptions)
