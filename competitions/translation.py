from modeltranslation.translator import TranslationOptions, translator

from .models import CompetitionResult, CompetitionType, SchoolHonor


class CompetitionTypeTranslationOptions(TranslationOptions):
    fields = ("name",)


class CompetitionResultTranslationOptions(TranslationOptions):
    fields = ("title", "location", "result_place", "description")


class SchoolHonorTranslationOptions(TranslationOptions):
    fields = ("title", "description")


translator.register(CompetitionType, CompetitionTypeTranslationOptions)
translator.register(CompetitionResult, CompetitionResultTranslationOptions)
translator.register(SchoolHonor, SchoolHonorTranslationOptions)
