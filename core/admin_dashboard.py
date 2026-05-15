from __future__ import annotations

from dataclasses import dataclass

from django.contrib.admin.models import LogEntry
from django.db.utils import OperationalError, ProgrammingError
from django.urls import NoReverseMatch, reverse
from django.utils import timezone


@dataclass(frozen=True)
class DashboardCard:
    title: str
    value: int
    subtitle: str
    icon: str
    link: str


@dataclass(frozen=True)
class DashboardLink:
    title: str
    icon: str
    link: str


def _safe_reverse(name: str, *args) -> str:
    try:
        return reverse(name, args=args)
    except NoReverseMatch:
        return "#"


def _count(qs) -> int:
    try:
        return int(qs.count())
    except Exception:
        return 0


def dashboard(request, context: dict) -> dict:
    """
    Unfold dashboard callback.
    Signature: (request, context) -> context
    """

    cards: list[DashboardCard] = []
    quick_links: list[DashboardLink] = []

    try:
        from people.models import SchoolClass, Staff, Student
        from news.models import NewsPost
        from clubs.models import Club
        from site_content.models import CampusMapZone, GalleryAlbum
        from events_school.models import SchoolEvent
        from events_extracurricular.models import ExtracurricularEvent
    except Exception:
        SchoolClass = Staff = Student = NewsPost = Club = GalleryAlbum = CampusMapZone = SchoolEvent = ExtracurricularEvent = None

    try:
        if Student:
            cards.append(
                DashboardCard(
                    title="Ученики",
                    value=_count(Student.objects.all()),
                    subtitle="Записей в базе",
                    icon="school",
                    link=_safe_reverse("admin:people_student_changelist"),
                )
            )
        if Staff:
            cards.append(
                DashboardCard(
                    title="Сотрудники",
                    value=_count(Staff.objects.all()),
                    subtitle="Профили персонала",
                    icon="badge",
                    link=_safe_reverse("admin:people_staff_changelist"),
                )
            )
        if SchoolClass:
            cards.append(
                DashboardCard(
                    title="Классы",
                    value=_count(SchoolClass.objects.all()),
                    subtitle="Активные и архивные",
                    icon="class",
                    link=_safe_reverse("admin:people_schoolclass_changelist"),
                )
            )
        if NewsPost:
            total_news = _count(NewsPost.objects.all())
            draft_news = _count(NewsPost.objects.filter(published_at__gt=timezone.now()))
            cards.append(
                DashboardCard(
                    title="Новости",
                    value=total_news,
                    subtitle=f"Запланировано: {draft_news}",
                    icon="newspaper",
                    link=_safe_reverse("admin:news_newspost_changelist"),
                )
            )
        if Club:
            cards.append(
                DashboardCard(
                    title="Клубы",
                    value=_count(Club.objects.all()),
                    subtitle="Внеклассные активности",
                    icon="groups",
                    link=_safe_reverse("admin:clubs_club_changelist"),
                )
            )
        if SchoolEvent:
            cards.append(
                DashboardCard(
                    title="События (школа)",
                    value=_count(SchoolEvent.objects.all()),
                    subtitle="Школьные мероприятия",
                    icon="event",
                    link=_safe_reverse("admin:events_school_schoolevent_changelist"),
                )
            )
        if ExtracurricularEvent:
            cards.append(
                DashboardCard(
                    title="События (внеурочные)",
                    value=_count(ExtracurricularEvent.objects.all()),
                    subtitle="Кружки, секции",
                    icon="sports_handball",
                    link=_safe_reverse("admin:events_extracurricular_extracurricularevent_changelist"),
                )
            )
        if GalleryAlbum:
            cards.append(
                DashboardCard(
                    title="Галерея",
                    value=_count(GalleryAlbum.objects.all()),
                    subtitle="Альбомы сайта",
                    icon="photo_library",
                    link=_safe_reverse("admin:site_content_galleryalbum_changelist"),
                )
            )
        if CampusMapZone:
            cards.append(
                DashboardCard(
                    title="Карта кампуса",
                    value=_count(CampusMapZone.objects.all()),
                    subtitle="Зоны интерактивной карты",
                    icon="map",
                    link=_safe_reverse("admin:site_content_campusmapzone_changelist"),
                )
            )
    except (OperationalError, ProgrammingError):
        pass

    quick_links.extend(
        [
            DashboardLink("Добавить новость", "add_circle", _safe_reverse("admin:news_newspost_add")),
            DashboardLink("Добавить событие", "add_circle", _safe_reverse("admin:events_school_schoolevent_add")),
            DashboardLink("Добавить альбом", "add_photo_alternate", _safe_reverse("admin:site_content_galleryalbum_add")),
            DashboardLink("Карта кампуса", "map", _safe_reverse("admin:site_content_campusmapzone_changelist")),
            DashboardLink("Меню сайта", "menu", _safe_reverse("admin:navigation_menuitem_changelist")),
            DashboardLink("Сообщения", "mail", _safe_reverse("admin:contacts_contactmessage_changelist")),
        ]
    )

    recent = []
    try:
        entries = (
            LogEntry.objects.select_related("user", "content_type")
            .order_by("-action_time")
            .only(
                "action_time",
                "user__username",
                "object_repr",
                "content_type__app_label",
                "content_type__model",
                "object_id",
                "action_flag",
            )[:12]
        )
        for e in entries:
            icon = "edit"
            if e.action_flag == 1:
                icon = "add"
            elif e.action_flag == 3:
                icon = "delete"

            link = None
            if e.content_type_id and e.object_id:
                link = _safe_reverse(
                    f"admin:{e.content_type.app_label}_{e.content_type.model}_change",
                    e.object_id,
                )
                if link == "#":
                    link = None

            recent.append(
                {
                    "when": timezone.localtime(e.action_time) if e.action_time else None,
                    "user": getattr(e.user, "username", "") or "",
                    "title": e.object_repr,
                    "model": f"{e.content_type.app_label}.{e.content_type.model}" if e.content_type_id else "",
                    "icon": icon,
                    "link": link,
                }
            )
    except Exception:
        recent = []

    context["dashboard_cards"] = cards
    context["dashboard_quick_links"] = quick_links
    context["dashboard_recent"] = recent
    context["dashboard_now"] = timezone.localtime(timezone.now())
    return context
