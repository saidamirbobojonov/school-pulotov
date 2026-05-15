from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath

from django import template
from django.core.files.storage import default_storage

register = template.Library()


@dataclass(frozen=True)
class ResponsiveCandidates:
    src: str
    srcset: str


def _variant_name(original_name: str, width: int) -> str:
    p = PurePosixPath(original_name)
    return str(p.with_name(f"{p.stem}-{width}w{p.suffix}"))


@register.simple_tag
def responsive_candidates(image_field_file, widths: str = "360,720,1080") -> ResponsiveCandidates:
    """
    Returns (src, srcset) for an ImageFieldFile, based on generated variants:
      original:  foo.jpg
      variants:  foo-360w.jpg, foo-720w.jpg, foo-1080w.jpg

    If no variants exist, falls back to original only.
    """
    if not image_field_file:
        return ResponsiveCandidates(src="", srcset="")

    original_name = getattr(image_field_file, "name", "") or ""
    original_url = getattr(image_field_file, "url", "") or ""
    if not original_name or not original_url:
        return ResponsiveCandidates(src=original_url, srcset="")

    try:
        width_values = [int(x.strip()) for x in widths.split(",") if x.strip()]
    except ValueError:
        width_values = [360, 720, 1080]

    candidates: list[tuple[int, str]] = []
    for w in sorted(set(width_values)):
        variant = _variant_name(original_name, w)
        if default_storage.exists(variant):
            try:
                candidates.append((w, default_storage.url(variant)))
            except Exception:
                continue

    if not candidates:
        return ResponsiveCandidates(src=original_url, srcset="")

    srcset = ", ".join([f"{url} {w}w" for (w, url) in candidates])
    # Keep original as fallback `src` (typically the largest / highest-quality).
    return ResponsiveCandidates(src=original_url, srcset=srcset)


@register.simple_tag
def responsive_url(image_field_file, width: int) -> str:
    """
    Returns the URL of a responsive variant (foo-64w.png). Falls back to original URL.
    """
    if not image_field_file:
        return ""
    original_name = getattr(image_field_file, "name", "") or ""
    original_url = getattr(image_field_file, "url", "") or ""
    if not original_name:
        return original_url
    variant = _variant_name(original_name, int(width))
    if default_storage.exists(variant):
        try:
            return default_storage.url(variant)
        except Exception:
            return original_url
    return original_url
