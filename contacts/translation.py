from modeltranslation.translator import TranslationOptions, translator

from .models import ContactPage


class ContactPageTranslationOptions(TranslationOptions):
    fields = ("address", "address_2", "working_hours")


translator.register(ContactPage, ContactPageTranslationOptions)
