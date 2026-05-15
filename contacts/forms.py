from __future__ import annotations

from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

from .models import AdmissionApplication, ContactMessage


def _clean_text(value: str) -> str:
    value = strip_tags(value or "")
    return " ".join(value.split()).strip()


def _validate_upload(file) -> None:
    if not file:
        return

    max_bytes = 10 * 1024 * 1024
    if getattr(file, "size", 0) > max_bytes:
        raise ValidationError("File is too large (max 10MB).")

    name = (getattr(file, "name", "") or "").lower()
    allowed_ext = (".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png")
    if not name.endswith(allowed_ext):
        raise ValidationError("Unsupported file type.")


class ContactMessageForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactMessage
        fields = ("name", "email", "phone", "subject", "message")

    def clean(self):
        cleaned = super().clean()
        if (cleaned.get("website") or "").strip():
            raise ValidationError("Invalid submission.")
        return cleaned

    def clean_name(self) -> str:
        return _clean_text(self.cleaned_data.get("name", ""))

    def clean_subject(self) -> str:
        return _clean_text(self.cleaned_data.get("subject", ""))

    def clean_message(self) -> str:
        return _clean_text(self.cleaned_data.get("message", ""))


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        if not data:
            return []
        if not isinstance(data, (list, tuple)):
            data = [data]
        return [super().clean(item, initial) for item in data]


class AdmissionApplicationForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)
    documents = MultipleFileField(required=False, validators=[_validate_upload])

    class Meta:
        model = AdmissionApplication
        fields = ("student_name", "parent_name", "email", "phone", "grade", "note")

    def clean(self):
        cleaned = super().clean()
        if (cleaned.get("website") or "").strip():
            raise ValidationError("Invalid submission.")
        return cleaned

    def clean_student_name(self) -> str:
        return _clean_text(self.cleaned_data.get("student_name", ""))

    def clean_parent_name(self) -> str:
        return _clean_text(self.cleaned_data.get("parent_name", ""))

    def clean_note(self) -> str:
        return _clean_text(self.cleaned_data.get("note", ""))

