from __future__ import annotations

from django.templatetags.static import static
from django.db.utils import OperationalError, ProgrammingError
from django.contrib import admin
from django.urls import NoReverseMatch, reverse
from django.utils.text import capfirst
import re


def admin_site_header(request) -> str:
    try:
        from site_content.models import SchoolName

        info = SchoolName.objects.first()
        if info and getattr(info, "name", None):
            return str(info.name)
    except (OperationalError, ProgrammingError):
        pass
    except Exception:
        return "Админ-панель"
    return "Админ-панель"


def admin_site_icon(request):
    """
    Unfold supports a string URL or {"light": "...", "dark": "..."}.
    """
    try:
        from site_content.models import SchoolName

        info = SchoolName.objects.first()
        image = getattr(info, "image", None) if info else None
        url = getattr(image, "url", None) if image else None
        if url:
            return {"light": url, "dark": url}
    except (OperationalError, ProgrammingError):
        pass
    except Exception:
        return None
    return None


def admin_custom_style(request) -> str:
    return static("admin/custom.css")


def admin_site_logo(request):
    """
    Optional logo for the sidebar header.
    Returns a string URL or {"light": "...", "dark": "..."}.
    """
    try:
        from site_content.models import SchoolName

        info = SchoolName.objects.first()
        image = getattr(info, "image", None) if info else None
        url = getattr(image, "url", None) if image else None
        if url:
            return {"light": url, "dark": url}
    except (OperationalError, ProgrammingError):
        pass
    except Exception:
        return None
    return None


def _base_sidebar_navigation():
    return [
        {
            "title": "Сайт",
            "collapsible": True,
            "items": [
                {"title": "Панель управления", "icon": "dashboard", "link": "/admin/"},
                {"title": "Меню", "icon": "menu", "link": "/admin/navigation/menuitem/"},
                {"title": "Хиро-блоки", "icon": "view_quilt", "link": "/admin/site_content/hero/"},
                {"title": "Объявления", "icon": "campaign", "link": "/admin/site_content/announcement/"},
                {"title": "Галерея", "icon": "photo_library", "link": "/admin/site_content/galleryalbum/"},
                {"title": "Слоганы", "icon": "format_quote", "link": "/admin/site_content/slogan/"},
                {"title": "Карта кампуса", "icon": "map", "link": "/admin/site_content/campusmapzone/"},
                {"title": "Соцсети", "icon": "share", "link": "/admin/site_content/socialnetwork/"},
                {"title": "О школе (контент)", "icon": "info", "link": "/admin/site_content/schoolcontent/"},
                {"title": "Название школы", "icon": "school", "link": "/admin/site_content/schoolname/"},
                {"title": "Страница Admissions", "icon": "how_to_reg", "link": "/admin/site_content/admissionspage/"},
                {"title": "FAQ", "icon": "help", "link": "/admin/site_content/faqitem/"},
            ],
        },
        {
            "title": "Контент",
            "collapsible": True,
            "separator": True,
            "items": [
                {"title": "Новости", "icon": "newspaper", "link": "/admin/news/newspost/"},
                {"title": "Клубы", "icon": "groups", "link": "/admin/clubs/club/"},
                {"title": "События (школьные)", "icon": "event", "link": "/admin/events_school/schoolevent/"},
                {"title": "Посты событий (школьные)", "icon": "feed", "link": "/admin/events_school/schooleventpost/"},
                {"title": "Категории событий (школьные)", "icon": "category", "link": "/admin/events_school/schooleventcategory/"},
                {"title": "События (внеурочные)", "icon": "sports_handball", "link": "/admin/events_extracurricular/extracurricularevent/"},
                {"title": "Посты (внеурочные)", "icon": "feed", "link": "/admin/events_extracurricular/extracurricularpost/"},
                {"title": "Категории (внеурочные)", "icon": "category", "link": "/admin/events_extracurricular/extracurricularcategory/"},
                {"title": "Расписание внешкольных занятий", "icon": "schedule", "link": "/admin/events_extracurricular/extracurricularschedule/"},
                {"title": "Достижения", "icon": "emoji_events", "link": "/admin/competitions/competitionresult/"},
                {"title": "Почёт школы", "icon": "military_tech", "link": "/admin/competitions/schoolhonor/"},
            ],
        },
        {
            "title": "Учёба и люди",
            "collapsible": True,
            "separator": True,
            "items": [
                {"title": "Классы", "icon": "class", "link": "/admin/people/schoolclass/"},
                {"title": "Ученики", "icon": "school", "link": "/admin/people/student/"},
                {"title": "Сотрудники", "icon": "badge", "link": "/admin/people/staff/"},
                {"title": "Родительский комитет", "icon": "groups", "link": "/admin/site_content/parentscommitteepage/"},
                {"title": "Методический отдел", "icon": "school", "link": "/admin/site_content/teacherscommitteepage/"},
                {"title": "Предметы", "icon": "menu_book", "link": "/admin/people/subject/"},
                {"title": "Локации выпускников", "icon": "public", "link": "/admin/people/graduatedestination/"},
                {"title": "Выпускники за рубежом", "icon": "travel_explore", "link": "/admin/people/graduatestudyrecord/"},
                {"title": "Кабинеты", "icon": "meeting_room", "link": "/admin/academics/room/"},
                {"title": "Временные слоты", "icon": "schedule", "link": "/admin/academics/timeslot/"},
                {"title": "Расписание уроков", "icon": "calendar_view_week", "link": "/admin/academics/classlesson/"},
                {"title": "Планы уроков", "icon": "description", "link": "/admin/academics/lessonplan/"},
                {"title": "Материалы уроков", "icon": "auto_stories", "link": "/admin/academics/lessonmaterial/"},
                {"title": "Задания", "icon": "assignment", "link": "/admin/academics/classassignment/"},
                {"title": "Материалы заданий", "icon": "attach_file", "link": "/admin/academics/assignmentmaterial/"},
            ],
        },
        {
            "title": "Заявки и сообщения",
            "collapsible": True,
            "separator": True,
            "items": [
                {"title": "Контакты (страница)", "icon": "contact_page", "link": "/admin/contacts/contactpage/"},
                {"title": "Сообщения", "icon": "mail", "link": "/admin/contacts/contactmessage/"},
                {"title": "Заявки на поступление", "icon": "assignment_ind", "link": "/admin/contacts/admissionapplication/"},
            ],
        },
        {
            "title": "Доступ",
            "collapsible": True,
            "separator": True,
            "items": [
                {"title": "Пользователи", "icon": "manage_accounts", "link": "/admin/accounts/user/"},
                {"title": "Группы", "icon": "group", "link": "/admin/auth/group/"},
            ],
        },
    ]


def _collect_nav_models(items, target: set[tuple[str, str]]):
    for item in items:
        link = item.get("link")
        if isinstance(link, str):
            match = re.match(r"^/admin/([^/]+)/([^/]+)/", link)
            if match:
                target.add((match.group(1), match.group(2)))
        if "items" in item:
            _collect_nav_models(item["items"], target)


def sidebar_navigation(request):
    base_navigation = _base_sidebar_navigation()
    used_models: set[tuple[str, str]] = set()
    for group in base_navigation:
        _collect_nav_models(group.get("items", []), used_models)

    other_items = []
    try:
        for model, model_admin in admin.site._registry.items():
            app_label = model._meta.app_label
            model_name = model._meta.model_name
            if (app_label, model_name) in used_models:
                continue
            if not model_admin.has_module_permission(request):
                continue
            perms = model_admin.get_model_perms(request)
            if not any(perms.values()):
                continue
            try:
                link = reverse(f"admin:{app_label}_{model_name}_changelist")
            except NoReverseMatch:
                continue
            other_items.append(
                {
                    "title": capfirst(model._meta.verbose_name_plural),
                    "icon": "widgets",
                    "link": link,
                }
            )
    except Exception:
        other_items = []

    if other_items:
        other_items.sort(key=lambda item: item["title"])
        base_navigation.append(
            {
                "title": "Other",
                "collapsible": True,
                "separator": True,
                "items": other_items,
            }
        )

    return base_navigation
