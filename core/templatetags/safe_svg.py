from __future__ import annotations

import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


_UNSAFE_TAGS = ("script", "foreignobject", "iframe", "object", "embed", "link", "meta")
_UNSAFE_PREFIXES = ("javascript:", "data:text/html")
_EVENT_HANDLER_RE = re.compile(r"\bon[a-z0-9_-]+\s*=", re.IGNORECASE)


@register.filter
def safe_svg(value: object) -> str:
    """
    Best-effort sanitizer for inline SVG stored in the database.

    If content looks unsafe (scripts, event handlers, foreignObject, etc) we
    render nothing instead of injecting raw HTML.
    """
    if not value:
        return ""

    svg = str(value).strip()
    if not svg:
        return ""
    if len(svg) > 20_000:
        return ""

    lowered = svg.lower()
    if "<svg" not in lowered or "</svg>" not in lowered:
        return ""
    if "<!doctype" in lowered or "<!entity" in lowered:
        return ""

    if _EVENT_HANDLER_RE.search(svg):
        return ""

    for bad in _UNSAFE_PREFIXES:
        if bad in lowered:
            return ""

    for tag in _UNSAFE_TAGS:
        if f"<{tag}" in lowered or f"</{tag}" in lowered:
            return ""

    return mark_safe(svg)

