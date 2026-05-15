from __future__ import annotations

from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def graduate_destinations(request: HttpRequest) -> JsonResponse:
    """
    Public read-only endpoint for the 3D globe on the About page.
    """
    try:
        from django.db.utils import OperationalError, ProgrammingError
        from django.db.models import Prefetch

        from .models import GraduateDestination, GraduateStudyRecord
    except Exception:
        return JsonResponse({"results": []})

    try:
        grads_qs = GraduateStudyRecord.objects.filter(is_public=True).order_by("order", "id")
        destinations = list(
            GraduateDestination.objects.filter(is_public=True)
            .prefetch_related(Prefetch("graduates", queryset=grads_qs))
            .order_by("country", "city", "id")
        )
    except (OperationalError, ProgrammingError):
        return JsonResponse({"results": []})

    results: list[dict] = []
    for d in destinations:
        grads = [
            {
                "id": g.id,
                "full_name": g.full_name,
                "photo_1_url": (g.photo_1.url if getattr(g, "photo_1", None) else ""),
                "photo_2_url": (g.photo_2.url if getattr(g, "photo_2", None) else ""),
                "graduation_year": g.graduation_year,
                "university_name": g.university_name,
                "program": g.program,
                "degree": g.degree,
                "start_year": g.start_year,
            }
            for g in d.graduates.all()
        ]

        results.append(
            {
                "id": d.id,
                "city": d.city,
                "country": d.country,
                "latitude": d.latitude,
                "longitude": d.longitude,
                "title": d.title,
                "description": d.description,
                "image_url": (d.image.url if d.image else ""),
                "assistant_url": d.assistant_url,
                "graduates_count": len(grads),
                "graduates": grads,
            }
        )

    return JsonResponse({"results": results})
