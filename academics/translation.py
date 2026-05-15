from modeltranslation.translator import TranslationOptions, translator

from .models import (
    AssignmentMaterial,
    ClassAssignment,
    LessonMaterial,
    LessonPlan,
    Room,
)


class RoomTranslationOptions(TranslationOptions):
    fields = ("name",)


class LessonPlanTranslationOptions(TranslationOptions):
    fields = ("title", "description")


class LessonMaterialTranslationOptions(TranslationOptions):
    fields = ("title",)


class ClassAssignmentTranslationOptions(TranslationOptions):
    fields = ("title", "description")


class AssignmentMaterialTranslationOptions(TranslationOptions):
    fields = ("title",)


translator.register(Room, RoomTranslationOptions)
translator.register(LessonPlan, LessonPlanTranslationOptions)
translator.register(LessonMaterial, LessonMaterialTranslationOptions)
translator.register(ClassAssignment, ClassAssignmentTranslationOptions)
translator.register(AssignmentMaterial, AssignmentMaterialTranslationOptions)
