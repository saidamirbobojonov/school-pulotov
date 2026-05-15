from __future__ import annotations

from django.contrib.admin import ModelAdmin as DjangoModelAdmin

from modeltranslation.admin import TranslationAdmin


try:
    from unfold.admin import ModelAdmin as UnfoldModelAdmin
except Exception:  # pragma: no cover
    UnfoldModelAdmin = DjangoModelAdmin


class UnfoldAdmin(UnfoldModelAdmin):
    pass


class TranslatableUnfoldAdmin(TranslationAdmin, UnfoldModelAdmin):
    pass

