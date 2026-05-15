from __future__ import annotations

from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

from people.models import Staff, Subject

from .models import AssignmentMaterial, ClassAssignment, LessonMaterial, LessonPlan


def _clean_text(value: str) -> str:
    value = strip_tags(value or "")
    return " ".join(value.split()).strip()


_INPUT_CLASS = (
    "w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 "
    "bg-white dark:bg-white/5 focus:ring-2 focus:ring-primary focus:border-primary "
    "dark:text-white outline-none transition-all"
)
_TEXTAREA_CLASS = (
    "w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 "
    "bg-white dark:bg-white/5 focus:ring-2 focus:ring-primary focus:border-primary "
    "dark:text-white outline-none transition-all min-h-[120px]"
)
_SELECT_CLASS = _INPUT_CLASS + " appearance-none cursor-pointer"
_CHECKBOX_CLASS = "rounded border-gray-300 text-primary focus:ring-primary"
_FILE_CLASS = (
    "block w-full text-sm text-gray-600 dark:text-gray-200 "
    "file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 "
    "file:bg-primary file:text-white hover:file:bg-primary-dark"
)


def _apply_widget_styles(form: forms.Form) -> None:
    for name, field in form.fields.items():
        widget = field.widget
        attrs = widget.attrs
        if isinstance(widget, forms.Textarea):
            attrs.setdefault("class", _TEXTAREA_CLASS)
        elif isinstance(widget, forms.Select):
            attrs.setdefault("class", _SELECT_CLASS)
        elif isinstance(widget, forms.CheckboxInput):
            attrs.setdefault("class", _CHECKBOX_CLASS)
        elif isinstance(widget, forms.ClearableFileInput):
            attrs.setdefault("class", _FILE_CLASS)
        else:
            attrs.setdefault("class", _INPUT_CLASS)
        widget.attrs = attrs


def _validate_upload(file, *, max_mb: int = 50) -> None:
    if not file:
        return
    max_bytes = max_mb * 1024 * 1024
    if getattr(file, "size", 0) > max_bytes:
        raise ValidationError(f"File is too large (max {max_mb}MB).")


class LessonPlanCreateForm(forms.ModelForm):
    class Meta:
        model = LessonPlan
        fields = (
            "grade",
            "subject",
            "title_ru",
            "title_tg",
            "title_en",
            "date",
            "description_ru",
            "description_tg",
            "description_en",
            "is_published",
        )

    def __init__(self, *args, staff: Staff | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.staff = staff

        self.fields["subject"].queryset = Subject.objects.all().order_by("name")

        if staff and staff.subjects.exists():
            self.fields["subject"].queryset = staff.subjects.all().order_by("name")

        for name in self.fields:
            self.fields[name].required = name in {"grade", "subject", "title_ru", "title_tg", "title_en"}

        self.fields["date"].widget = forms.DateInput(attrs={"type": "date"})
        _apply_widget_styles(self)

    def clean_title_ru(self) -> str:
        return _clean_text(self.cleaned_data.get("title_ru", ""))

    def clean_title_tg(self) -> str:
        return _clean_text(self.cleaned_data.get("title_tg", ""))

    def clean_title_en(self) -> str:
        return _clean_text(self.cleaned_data.get("title_en", ""))

    def clean_description_ru(self) -> str:
        return _clean_text(self.cleaned_data.get("description_ru", ""))

    def clean_description_tg(self) -> str:
        return _clean_text(self.cleaned_data.get("description_tg", ""))

    def clean_description_en(self) -> str:
        return _clean_text(self.cleaned_data.get("description_en", ""))

    def save(self, commit: bool = True):
        obj: LessonPlan = super().save(commit=False)
        obj.title = self.cleaned_data.get("title_ru") or self.cleaned_data.get("title_en") or self.cleaned_data.get("title_tg") or ""
        obj.description = (
            self.cleaned_data.get("description_ru")
            or self.cleaned_data.get("description_en")
            or self.cleaned_data.get("description_tg")
            or ""
        )
        if self.staff:
            obj.teacher = self.staff
        if commit:
            obj.save()
            self.save_m2m()
        return obj


class LessonMaterialCreateForm(forms.ModelForm):
    class Meta:
        model = LessonMaterial
        fields = ("lesson_plan", "title_ru", "title_tg", "title_en", "file", "youtube_link", "external_link")

    def __init__(self, *args, staff: Staff | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.staff = staff

        qs = LessonPlan.objects.all().order_by("-date", "-created_at", "-id")
        if staff:
            qs = qs.filter(teacher=staff)
        self.fields["lesson_plan"].queryset = qs

        for field in ("file", "youtube_link", "external_link"):
            self.fields[field].required = False

        _apply_widget_styles(self)

    def clean_title_ru(self) -> str:
        return _clean_text(self.cleaned_data.get("title_ru", ""))

    def clean_title_tg(self) -> str:
        return _clean_text(self.cleaned_data.get("title_tg", ""))

    def clean_title_en(self) -> str:
        return _clean_text(self.cleaned_data.get("title_en", ""))

    def clean_file(self):
        file = self.cleaned_data.get("file")
        _validate_upload(file, max_mb=50)
        return file

    def clean(self):
        cleaned = super().clean()
        file = cleaned.get("file")
        yt = (cleaned.get("youtube_link") or "").strip()
        link = (cleaned.get("external_link") or "").strip()
        if not file and not yt and not link:
            raise ValidationError("Add a file or a link (YouTube/external).")
        return cleaned

    def save(self, commit: bool = True):
        obj: LessonMaterial = super().save(commit=False)
        obj.title = self.cleaned_data.get("title_ru") or self.cleaned_data.get("title_en") or self.cleaned_data.get("title_tg") or ""
        if commit:
            obj.save()
            self.save_m2m()
        return obj


class ClassAssignmentCreateForm(forms.ModelForm):
    class Meta:
        model = ClassAssignment
        fields = (
            "grade",
            "subject",
            "title_ru",
            "title_tg",
            "title_en",
            "description_ru",
            "description_tg",
            "description_en",
            "assigned_at",
            "due_at",
            "is_published",
        )

    def __init__(self, *args, staff: Staff | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.staff = staff

        self.fields["subject"].queryset = Subject.objects.all().order_by("name")
        self.fields["subject"].required = False

        if staff and staff.subjects.exists():
            self.fields["subject"].queryset = staff.subjects.all().order_by("name")

        for name in self.fields:
            self.fields[name].required = name in {"grade", "title_ru", "title_tg", "title_en"}

        self.fields["assigned_at"].widget = forms.DateInput(attrs={"type": "date"})
        self.fields["due_at"].widget = forms.DateInput(attrs={"type": "date"})
        _apply_widget_styles(self)

    def clean_title_ru(self) -> str:
        return _clean_text(self.cleaned_data.get("title_ru", ""))

    def clean_title_tg(self) -> str:
        return _clean_text(self.cleaned_data.get("title_tg", ""))

    def clean_title_en(self) -> str:
        return _clean_text(self.cleaned_data.get("title_en", ""))

    def clean_description_ru(self) -> str:
        return _clean_text(self.cleaned_data.get("description_ru", ""))

    def clean_description_tg(self) -> str:
        return _clean_text(self.cleaned_data.get("description_tg", ""))

    def clean_description_en(self) -> str:
        return _clean_text(self.cleaned_data.get("description_en", ""))

    def save(self, commit: bool = True):
        obj: ClassAssignment = super().save(commit=False)
        obj.title = self.cleaned_data.get("title_ru") or self.cleaned_data.get("title_en") or self.cleaned_data.get("title_tg") or ""
        obj.description = (
            self.cleaned_data.get("description_ru")
            or self.cleaned_data.get("description_en")
            or self.cleaned_data.get("description_tg")
            or ""
        )
        if self.staff:
            obj.teacher = self.staff
        if commit:
            obj.save()
            self.save_m2m()
        return obj


class AssignmentMaterialCreateForm(forms.ModelForm):
    class Meta:
        model = AssignmentMaterial
        fields = ("assignment", "title_ru", "title_tg", "title_en", "file", "youtube_link", "external_link")

    def __init__(self, *args, staff: Staff | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.staff = staff

        qs = ClassAssignment.objects.all().order_by("-assigned_at", "-created_at", "-id")
        if staff:
            qs = qs.filter(teacher=staff)
        self.fields["assignment"].queryset = qs

        for field in ("file", "youtube_link", "external_link"):
            self.fields[field].required = False

        _apply_widget_styles(self)

    def clean_title_ru(self) -> str:
        return _clean_text(self.cleaned_data.get("title_ru", ""))

    def clean_title_tg(self) -> str:
        return _clean_text(self.cleaned_data.get("title_tg", ""))

    def clean_title_en(self) -> str:
        return _clean_text(self.cleaned_data.get("title_en", ""))

    def clean_file(self):
        file = self.cleaned_data.get("file")
        _validate_upload(file, max_mb=50)
        return file

    def clean(self):
        cleaned = super().clean()
        file = cleaned.get("file")
        yt = (cleaned.get("youtube_link") or "").strip()
        link = (cleaned.get("external_link") or "").strip()
        if not file and not yt and not link:
            raise ValidationError("Add a file or a link (YouTube/external).")
        return cleaned

    def save(self, commit: bool = True):
        obj: AssignmentMaterial = super().save(commit=False)
        obj.title = self.cleaned_data.get("title_ru") or self.cleaned_data.get("title_en") or self.cleaned_data.get("title_tg") or ""
        if commit:
            obj.save()
            self.save_m2m()
        return obj
