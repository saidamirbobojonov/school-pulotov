from __future__ import annotations

from typing import Any


def page_has_other_pages(page_obj: Any) -> bool:
    """
    Return pagination state for Django and non-Django page-like objects.
    """
    has_other_pages = getattr(page_obj, "has_other_pages", None)
    if callable(has_other_pages):
        return bool(has_other_pages())
    if has_other_pages is not None:
        return bool(has_other_pages)

    for attr_name in ("has_next", "has_previous"):
        attr = getattr(page_obj, attr_name, None)
        if callable(attr):
            if bool(attr()):
                return True
        elif attr is not None and bool(attr):
            return True

    paginator = getattr(page_obj, "paginator", None)
    num_pages = getattr(paginator, "num_pages", None)
    if isinstance(num_pages, int):
        return num_pages > 1

    return False
