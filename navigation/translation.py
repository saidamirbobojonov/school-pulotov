from modeltranslation.translator import TranslationOptions, translator

from .models import MenuItem


class MenuItemTranslationOptions(TranslationOptions):
    fields = ("title",)


translator.register(MenuItem, MenuItemTranslationOptions)
