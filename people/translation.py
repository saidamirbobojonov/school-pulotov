from modeltranslation.translator import TranslationOptions, translator

from .models import GraduateDestination, GraduateStudyRecord, Staff, Student, Subject


class SubjectTranslationOptions(TranslationOptions):
    fields = ("name",)


translator.register(Subject, SubjectTranslationOptions)


class StaffTranslationOptions(TranslationOptions):
    fields = ("full_name", "position", "bio")


class StudentTranslationOptions(TranslationOptions):
    fields = ("full_name",)


translator.register(Staff, StaffTranslationOptions)
translator.register(Student, StudentTranslationOptions)


class GraduateDestinationTranslationOptions(TranslationOptions):
    fields = ("city", "country", "title", "description")


class GraduateStudyRecordTranslationOptions(TranslationOptions):
    fields = ("full_name", "university_name", "program", "degree")


translator.register(GraduateDestination, GraduateDestinationTranslationOptions)
translator.register(GraduateStudyRecord, GraduateStudyRecordTranslationOptions)
