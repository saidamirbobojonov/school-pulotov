from __future__ import annotations

import re

from django import template

register = template.Library()


@register.filter
def before_quotes(value: str | None) -> str:
    if not value:
        return ""
    return re.split(r'["«]', value)[0].strip()


@register.filter
def with_quotes(value: str | None) -> str:
    if not value:
        return ""
    match = re.search(r'(["«].*?["»])', value)
    return match.group(1) if match else ""


@register.filter
def get_item(mapping, key):
    if mapping is None:
        return ""
    try:
        return mapping.get(key, "")
    except AttributeError:
        try:
            return mapping[key]
        except Exception:
            return ""
