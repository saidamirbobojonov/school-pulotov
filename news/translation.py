from modeltranslation.translator import TranslationOptions, translator

from .models import NewsGallery, NewsPost


class NewsPostTranslationOptions(TranslationOptions):
    fields = ("title", "body")


class NewsGalleryTranslationOptions(TranslationOptions):
    fields = ("caption",)


translator.register(NewsPost, NewsPostTranslationOptions)
translator.register(NewsGallery, NewsGalleryTranslationOptions)
