from __future__ import annotations

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User


class PortalAuthenticationForm(AuthenticationForm):
    grade = forms.IntegerField(
        label=_("Grade"),
        required=False,
        min_value=1,
        max_value=11,
    )

    def clean(self):
        grade = self.cleaned_data.get("grade")
        username = (self.cleaned_data.get("username") or "").strip()

        if grade and not username:
            try:
                user = User.objects.get(role=User.Role.STUDENT, grade=grade)
            except User.DoesNotExist as exc:
                raise ValidationError(_("No portal account exists for this grade.")) from exc
            self.cleaned_data["username"] = user.get_username()

        return super().clean()
