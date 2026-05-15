from __future__ import annotations

import time

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db import close_old_connections
from django.db.models import Count, Prefetch
from django.db.utils import OperationalError, ProgrammingError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.generic import TemplateView

from core.pagination import page_has_other_pages


class PublicPageView(TemplateView):
    pass


class EmployeesPageView(TemplateView):
    template_name = "employees.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["founder"] = None
        context["role_groups"] = []

        from people.models import Staff

        title_by_role = dict(Staff.ROLE_CHOICES)
        max_attempts = 6
        for attempt in range(max_attempts):
            try:
                staff_members = list(Staff.objects.all().order_by("order", "full_name", "id"))

                founder = next((member for member in staff_members if member.role == "founder"), None)
                if founder:
                    context["founder"] = founder

                grouped_members: dict[str, list[Staff]] = {
                    "admin": [],
                    "teacher": [],
                    "staff": [],
                }
                role_aliases = {
                    "worker": "staff",
                    "workers": "staff",
                }

                for member in staff_members:
                    if founder and member.pk == founder.pk:
                        continue
                    normalized_role = role_aliases.get(member.role, member.role)
                    if normalized_role in grouped_members:
                        grouped_members[normalized_role].append(member)

                role_groups = []
                for role in ("admin", "teacher", "staff"):
                    members = grouped_members[role]
                    if members:
                        role_groups.append(
                            {
                                "role": role,
                                "title": title_by_role.get(role, role),
                                "members": members,
                            }
                        )

                context["role_groups"] = role_groups
                break
            except OperationalError as exc:
                # SQLite can be transiently locked right after admin writes.
                if "locked" in str(exc).lower() and attempt < (max_attempts - 1):
                    close_old_connections()
                    time.sleep(0.1 * (attempt + 1))
                    continue
                break
            except ProgrammingError:
                break

        return context


class SchedulesPageView(TemplateView):
    template_name = "schedules.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["classes"] = []
        context["grades"] = list(range(1, 12))
        context["selected_grade"] = None
        context["classes_in_grade"] = []
        context["weekdays"] = []
        context["time_slots"] = []
        context["schedule_blocks"] = []
        context["weekdays_note"] = ""

        try:
            from academics.models import ClassLesson, TimeSlot
            from people.models import SchoolClass

            classes = list(SchoolClass.objects.filter(is_active=True).order_by("grade", "name"))
            context["classes"] = classes

            selected_grade = None
            selected_grade_raw = (self.request.GET.get("grade") or "").strip()
            if selected_grade_raw.isdigit():
                selected_grade_num = int(selected_grade_raw)
                if 1 <= selected_grade_num <= 11:
                    selected_grade = selected_grade_num

            selected_id = (self.request.GET.get("class") or "").strip()
            if not selected_grade and selected_id.isdigit():
                selected_class = next((c for c in classes if c.pk == int(selected_id)), None)
                if selected_class:
                    selected_grade = selected_class.grade

            if not selected_grade and classes:
                selected_grade = classes[0].grade

            context["selected_grade"] = selected_grade

            classes_in_grade = [c for c in classes if c.grade == selected_grade] if selected_grade else []
            context["classes_in_grade"] = classes_in_grade

            time_slots = list(TimeSlot.objects.all().order_by("number"))
            context["time_slots"] = time_slots

            if selected_grade and classes_in_grade and time_slots:
                max_weekday = 5 if selected_grade <= 4 else 6
                weekday_labels = dict(ClassLesson.WEEKDAY_CHOICES)
                weekdays = [{"num": i, "label": weekday_labels.get(i, str(i))} for i in range(1, max_weekday + 1)]
                context["weekdays"] = weekdays
                if weekdays:
                    context["weekdays_note"] = _("%(first)s–%(last)s") % {
                        "first": weekdays[0]["label"],
                        "last": weekdays[-1]["label"],
                    }

                lessons = (
                    ClassLesson.objects.select_related("slot", "subject", "teacher", "room")
                    .filter(is_public=True, school_class__in=classes_in_grade, weekday__lte=max_weekday)
                    .order_by("school_class_id", "weekday", "slot__number")
                )
                grid: dict[tuple[int, int, int], ClassLesson] = {
                    (l.school_class_id, l.weekday, l.slot_id): l for l in lessons
                }

                schedule_blocks = []
                for school_class in classes_in_grade:
                    table_rows = []
                    for slot in time_slots:
                        cells = [grid.get((school_class.id, d["num"], slot.id)) for d in weekdays]
                        table_rows.append({"slot": slot, "cells": cells})
                    schedule_blocks.append(
                        {
                            "school_class": school_class,
                            "table_rows": table_rows,
                        }
                    )

                context["schedule_blocks"] = schedule_blocks
        except (OperationalError, ProgrammingError):
            pass

        return context


class AdmissionsPageView(TemplateView):
    template_name = "admissions.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["admissions_page"] = None
        context["admission_steps"] = []
        context["admission_dates"] = []
        context["application_form"] = None

        try:
            from site_content.models import AdmissionsPage

            page = AdmissionsPage.objects.prefetch_related("steps", "important_dates").first()
            context["admissions_page"] = page
            if page:
                context["admission_steps"] = list(page.steps.all().order_by("order", "id"))
                context["admission_dates"] = list(page.important_dates.all().order_by("order", "id"))
        except (OperationalError, ProgrammingError):
            pass

        try:
            from contacts.forms import AdmissionApplicationForm

            context["application_form"] = context.get("application_form") or AdmissionApplicationForm()
        except Exception:
            context["application_form"] = None

        return context


class MethodicalMaterialsPageView(TemplateView):
    template_name = "methodical-materials.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["materials"] = []

        try:
            from site_content.models import MethodicalMaterial

            context["materials"] = list(MethodicalMaterial.objects.all().order_by("-created_at", "-id"))
        except (OperationalError, ProgrammingError):
            pass

        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        from django.shortcuts import redirect
        from django.urls import reverse

        try:
            from contacts.forms import AdmissionApplicationForm
            from contacts.models import AdmissionApplicationDocument
        except Exception:
            return redirect(reverse("admissions"))

        if (request.POST.get("website") or "").strip():
            return redirect(f"{reverse('admissions')}?submitted=1")

        form = AdmissionApplicationForm(request.POST, request.FILES)
        if not form.is_valid():
            context = self.get_context_data(**kwargs)
            context["application_form"] = form
            return self.render_to_response(context)

        try:
            application = form.save()
            for file in form.cleaned_data.get("documents") or []:
                AdmissionApplicationDocument.objects.create(
                    application=application,
                    file=file,
                    original_name=getattr(file, "name", "") or "",
                )
        except (OperationalError, ProgrammingError):
            context = self.get_context_data(**kwargs)
            form.add_error(None, "Server is not ready. Please try again later.")
            context["application_form"] = form
            return self.render_to_response(context)

        return redirect(f"{reverse('admissions')}?submitted=1")


class ContactPageView(TemplateView):
    template_name = "contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            from contacts.forms import ContactMessageForm

            context["contact_form"] = context.get("contact_form") or ContactMessageForm()
        except Exception:
            context["contact_form"] = None
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        from django.shortcuts import redirect
        from django.urls import reverse

        try:
            from contacts.forms import ContactMessageForm
        except Exception:
            return redirect(reverse("contact"))

        if (request.POST.get("website") or "").strip():
            return redirect(f"{reverse('contact')}?sent=1")

        form = ContactMessageForm(request.POST)
        if not form.is_valid():
            context = self.get_context_data(**kwargs)
            context["contact_form"] = form
            return self.render_to_response(context)

        try:
            form.save()
        except (OperationalError, ProgrammingError):
            context = self.get_context_data(**kwargs)
            form.add_error(None, "Server is not ready. Please try again later.")
            context["contact_form"] = form
            return self.render_to_response(context)

        return redirect(f"{reverse('contact')}?sent=1")


class GalleryPageView(TemplateView):
    template_name = "gallery.html"
    paginate_by = 24

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["gallery_images"] = []
        context["gallery_albums"] = []
        context["active_album"] = ""
        context["page_obj"] = None
        context["paginator"] = None
        context["is_paginated"] = False
        context["querystring"] = ""

        try:
            from site_content.models import GalleryAlbum, GalleryImage

            active_album = (self.request.GET.get("album") or "").strip()

            counts = {
                item["album__slug"]: item["count"]
                for item in GalleryImage.objects.filter(is_public=True, album__is_public=True)
                .values("album__slug")
                .annotate(count=Count("id"))
            }

            album_qs = (
                GalleryAlbum.objects.filter(is_public=True)
                .prefetch_related(
                    Prefetch(
                        "images",
                        queryset=GalleryImage.objects.filter(is_public=True).order_by(
                            "order",
                            "-created_at",
                            "-id",
                        ),
                    )
                )
                .order_by("order", "id")
            )
            albums = []
            for album in album_qs:
                images = list(getattr(album, "images", []).all())
                cover = images[0] if images else None
                albums.append(
                    {
                        "slug": album.slug,
                        "title": album.title,
                        "count": counts.get(album.slug, 0),
                        "cover": cover,
                    }
                )

            context["gallery_albums"] = albums
            context["active_album"] = active_album

            if active_album:
                queryset = (
                    GalleryImage.objects.select_related("album")
                    .filter(is_public=True, album__is_public=True, album__slug=active_album)
                    .order_by("order", "-created_at", "-id")
                )

                paginator = Paginator(queryset, self.paginate_by)
                page_number = (self.request.GET.get("page") or "1").strip()
                page_obj = paginator.get_page(page_number)

                params = self.request.GET.copy()
                params.pop("page", None)
                qs = params.urlencode()

                context["gallery_images"] = list(page_obj.object_list)
                context["page_obj"] = page_obj
                context["paginator"] = paginator
                context["is_paginated"] = page_has_other_pages(page_obj)
                context["querystring"] = f"&{qs}" if qs else ""
        except (OperationalError, ProgrammingError):
            pass

        return context


class AboutPageView(TemplateView):
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["slogans"] = []
        context["clubs_preview"] = []
        context["competition_winners"] = []
        context["campus_map_zones"] = []
        context["campus_map_data"] = {}
        context["campus_map_default_zone"] = ""
        context["campus_map_default_title"] = ""
        context["campus_map_default_description"] = ""
        context["campus_map_default_image"] = ""
        context["education_types"] = []

        try:
            from site_content.models import Slogan

            context["slogans"] = list(Slogan.objects.filter(is_active=True).order_by("order", "id"))
        except (OperationalError, ProgrammingError):
            pass

        try:
            from site_content.models import EducationType

            context["education_types"] = list(EducationType.objects.filter(is_active=True).order_by("order", "id"))
        except (OperationalError, ProgrammingError):
            pass

        try:
            from site_content.models import CampusMapZone, CampusMapZonePart

            def read_i18n(obj, field: str) -> str:
                if not obj:
                    return ""
                for attr in (field, f"{field}_tg", f"{field}_ru", f"{field}_en"):
                    value = (getattr(obj, attr, "") or "").strip()
                    if value:
                        return value
                return ""

            zones = list(
                CampusMapZone.objects.filter(is_public=True, show_in_buttons=True)
                .prefetch_related(
                    Prefetch(
                        "parts",
                        queryset=CampusMapZonePart.objects.filter(is_public=True).order_by("order", "id"),
                    )
                )
                .order_by("order", "id")
            )
            context["campus_map_zones"] = zones

            map_data: dict[str, dict] = {}
            for zone in zones:
                parts = list(zone.parts.all())
                parts_payload = [
                    {
                        "title": read_i18n(p, "title"),
                        "description": read_i18n(p, "description"),
                        "image": p.image.url if getattr(p, "image", None) else "",
                    }
                    for p in parts
                    if read_i18n(p, "title") or read_i18n(p, "description") or getattr(p, "image", None)
                ]
                features = [p["title"] for p in parts_payload if p.get("title")]
                map_data[zone.zone] = {
                    "title": read_i18n(zone, "title"),
                    "description": read_i18n(zone, "description"),
                    "image": zone.image.url if zone.image else "",
                    "features": features,
                    "parts": parts_payload,
                    "is_clickable": bool(zone.is_clickable),
                }

            context["campus_map_data"] = map_data
        except (OperationalError, ProgrammingError):
            pass

        try:
            from clubs.models import Club

            context["clubs_preview"] = list(
                Club.objects.filter(is_public=True).order_by("name")[:4]
            )
        except (OperationalError, ProgrammingError):
            pass

        try:
            from competitions.models import CompetitionResult

            context["competition_winners"] = list(
                CompetitionResult.objects.select_related(
                    "competition_type",
                    "student",
                    "student__school_class",
                    "subject",
                ).order_by("-year", "-created_at", "-id")[:6]
            )
        except (OperationalError, ProgrammingError):
            pass

        return context


class RoleRequiredMixin(UserPassesTestMixin):
    allowed_roles: set[str] = set()
    raise_exception = True

    def test_func(self) -> bool:
        if not self.request.user.is_authenticated:
            return False
        if self.request.user.is_superuser:
            return True
        if self.request.user.is_staff:
            return True
        if not self.allowed_roles:
            return True
        return getattr(self.request.user, "role", None) in self.allowed_roles


def _get_student_class(request: HttpRequest):
    user = getattr(request, "user", None)
    if not user or getattr(user, "role", None) != "student":
        return None
    try:
        return user.student_profile.school_class
    except Exception:
        return None


def _get_student_grade(request: HttpRequest):
    user = getattr(request, "user", None)
    if not user or getattr(user, "role", None) != "student":
        return None
    try:
        student_class = user.student_profile.school_class
        return getattr(student_class, "grade", None)
    except Exception:
        pass
    return getattr(user, "grade", None)


def _get_staff_profile(request: HttpRequest):
    user = getattr(request, "user", None)
    if not user:
        return None
    try:
        return user.staff_profile
    except Exception:
        return None


class PortalResourcesView(LoginRequiredMixin, TemplateView):
    template_name = "secure/resources.html"

    paginate_by = 12

    def get_context_data(self, **kwargs):
        from django.db.models import Q
        from django.utils.translation import gettext as _

        context = super().get_context_data(**kwargs)

        context["items"] = []
        context["subjects"] = []
        context["grades"] = []
        context["selected_grade"] = None
        context["active_subject"] = ""
        context["active_kind"] = ""
        context["search_query"] = ""
        context["needs_profile"] = False
        context["total_items"] = 0
        context["page_obj"] = None
        context["paginator"] = None
        context["is_paginated"] = False
        context["querystring"] = ""

        student_class = _get_student_class(self.request)
        student_grade = _get_student_grade(self.request)
        is_student = getattr(self.request.user, "role", None) == "student"
        if is_student and not student_class and not student_grade:
            context["needs_profile"] = True
            return context

        try:
            from academics.models import AssignmentMaterial, LessonMaterial
            from people.models import Subject

            q = ((self.request.GET.get("q") or "").strip())[:100]
            active_subject = (self.request.GET.get("subject") or "").strip()
            active_kind = (self.request.GET.get("kind") or "").strip()

            grades = list(range(1, 12))
            subjects = list(Subject.objects.all().order_by("name"))

            selected_grade = None
            selected_id = (self.request.GET.get("class") or "").strip()
            if student_class:
                selected_grade = getattr(student_class, "grade", None)
            elif selected_id.isdigit():
                selected_grade = int(selected_id)
            elif is_student and student_grade:
                selected_grade = int(student_grade)

            lesson_qs = (
                LessonMaterial.objects.select_related(
                    "lesson_plan",
                    "lesson_plan__subject",
                    "lesson_plan__teacher",
                )
                .filter(lesson_plan__is_published=True)
                .order_by("-created_at", "-id")
            )
            assign_qs = (
                AssignmentMaterial.objects.select_related(
                    "assignment",
                    "assignment__subject",
                    "assignment__teacher",
                )
                .filter(assignment__is_published=True)
                .order_by("-created_at", "-id")
            )

            if selected_grade:
                lesson_qs = lesson_qs.filter(lesson_plan__grade=selected_grade)
                assign_qs = assign_qs.filter(assignment__grade=selected_grade)

            if active_subject.isdigit():
                sid = int(active_subject)
                lesson_qs = lesson_qs.filter(lesson_plan__subject_id=sid)
                assign_qs = assign_qs.filter(assignment__subject_id=sid)

            if q:
                lesson_qs = lesson_qs.filter(
                    Q(title__icontains=q)
                    | Q(lesson_plan__title__icontains=q)
                    | Q(lesson_plan__description__icontains=q)
                )
                assign_qs = assign_qs.filter(
                    Q(title__icontains=q)
                    | Q(assignment__title__icontains=q)
                    | Q(assignment__description__icontains=q)
                )

            if active_kind == "lesson":
                assign_qs = assign_qs.none()
            elif active_kind == "assignment":
                lesson_qs = lesson_qs.none()

            items = []
            for m in lesson_qs[:500]:
                plan = m.lesson_plan
                title = (m.title or "").strip() or plan.title
                if m.file:
                    url = m.file.url
                    action_kind = "download"
                    icon = "download"
                    file_name = m.file.name.rsplit("/", 1)[-1]
                elif m.youtube_link:
                    url = m.youtube_link
                    action_kind = "open"
                    icon = "play_circle"
                    file_name = _("YouTube")
                else:
                    url = m.external_link
                    action_kind = "open"
                    icon = "link"
                    file_name = _("Link")
                items.append(
                    {
                        "kind": "lesson",
                        "badge": _("Lesson material"),
                        "title": title,
                        "subject": plan.subject,
                        "teacher": plan.teacher,
                        "grade": plan.grade,
                        "created_at": m.created_at,
                        "url": url,
                        "action_kind": action_kind,
                        "icon": icon,
                        "file_name": file_name,
                    }
                )

            for m in assign_qs[:500]:
                assignment = m.assignment
                title = (m.title or "").strip() or assignment.title
                if m.file:
                    url = m.file.url
                    action_kind = "download"
                    icon = "download"
                    file_name = m.file.name.rsplit("/", 1)[-1]
                elif m.youtube_link:
                    url = m.youtube_link
                    action_kind = "open"
                    icon = "play_circle"
                    file_name = _("YouTube")
                else:
                    url = m.external_link
                    action_kind = "open"
                    icon = "link"
                    file_name = _("Link")
                items.append(
                    {
                        "kind": "assignment",
                        "badge": _("Extra task"),
                        "title": title,
                        "subject": assignment.subject,
                        "teacher": assignment.teacher,
                        "grade": assignment.grade,
                        "created_at": m.created_at,
                        "url": url,
                        "action_kind": action_kind,
                        "icon": icon,
                        "file_name": file_name,
                    }
                )

            items.sort(key=lambda x: (x["created_at"] or timezone.now()), reverse=True)

            paginator = Paginator(items, self.paginate_by)
            page_number = (self.request.GET.get("page") or "1").strip()
            page_obj = paginator.get_page(page_number)

            params = self.request.GET.copy()
            params.pop("page", None)
            querystring = params.urlencode()

            context["items"] = list(page_obj.object_list)
            context["subjects"] = subjects
            context["grades"] = [] if student_grade else grades
            context["selected_grade"] = selected_grade
            context["active_subject"] = active_subject
            context["active_kind"] = active_kind
            context["search_query"] = q
            context["page_obj"] = page_obj
            context["paginator"] = paginator
            context["is_paginated"] = page_has_other_pages(page_obj)
            context["total_items"] = paginator.count
            context["querystring"] = f"&{querystring}" if querystring else ""
        except (OperationalError, ProgrammingError):
            pass

        return context


class PortalPlansView(LoginRequiredMixin, TemplateView):
    template_name = "secure/plans.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        from django.db.models import Q

        context = super().get_context_data(**kwargs)

        context["plans"] = []
        context["subjects"] = []
        context["grades"] = []
        context["selected_grade"] = None
        context["active_subject"] = ""
        context["search_query"] = ""
        context["needs_profile"] = False
        context["total_plans"] = 0
        context["page_obj"] = None
        context["paginator"] = None
        context["is_paginated"] = False
        context["querystring"] = ""

        student_grade = _get_student_grade(self.request)
        is_student = getattr(self.request.user, "role", None) == "student"
        if is_student and not student_grade:
            context["needs_profile"] = True
            return context

        try:
            from academics.models import LessonPlan
            from people.models import Subject

            q = ((self.request.GET.get("q") or "").strip())[:100]
            active_subject = (self.request.GET.get("subject") or "").strip()

            grades = list(range(1, 12))
            subjects = list(Subject.objects.all().order_by("name"))

            selected_grade = None
            selected_id = (self.request.GET.get("class") or "").strip()
            if student_grade:
                selected_grade = int(student_grade)
            elif selected_id.isdigit():
                selected_grade = int(selected_id)

            qs = (
                LessonPlan.objects.select_related("subject", "teacher")
                .prefetch_related("materials")
                .filter(is_published=True)
                .order_by("-date", "-created_at", "-id")
            )

            if selected_grade:
                qs = qs.filter(grade=selected_grade)

            if active_subject.isdigit():
                qs = qs.filter(subject_id=int(active_subject))

            if q:
                qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

            paginator = Paginator(qs, self.paginate_by)
            page_number = (self.request.GET.get("page") or "1").strip()
            page_obj = paginator.get_page(page_number)

            params = self.request.GET.copy()
            params.pop("page", None)
            querystring = params.urlencode()

            context["plans"] = list(page_obj.object_list)
            context["subjects"] = subjects
            context["grades"] = [] if student_grade else grades
            context["selected_grade"] = selected_grade
            context["active_subject"] = active_subject
            context["search_query"] = q
            context["page_obj"] = page_obj
            context["paginator"] = paginator
            context["is_paginated"] = page_has_other_pages(page_obj)
            context["total_plans"] = paginator.count
            context["querystring"] = f"&{querystring}" if querystring else ""
        except (OperationalError, ProgrammingError):
            pass

        return context


class PortalExtracurricularSchedulesView(LoginRequiredMixin, TemplateView):
    template_name = "secure/extracurricular-schedules.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        from django.db.models import Q

        context = super().get_context_data(**kwargs)

        context["schedules"] = []
        context["grades"] = []
        context["selected_grade"] = None
        context["search_query"] = ""
        context["needs_profile"] = False
        context["total_schedules"] = 0
        context["page_obj"] = None
        context["paginator"] = None
        context["is_paginated"] = False
        context["querystring"] = ""

        student_grade = _get_student_grade(self.request)
        is_student = getattr(self.request.user, "role", None) == "student"
        if is_student and not student_grade:
            context["needs_profile"] = True
            return context

        try:
            from events_extracurricular.models import ExtracurricularSchedule, GRADE_CHOICES

            now = timezone.now()
            q = ((self.request.GET.get("q") or "").strip())[:100]

            grades = [value for value, _ in GRADE_CHOICES]
            selected_grade = None
            selected_id = (self.request.GET.get("class") or "").strip()
            if student_grade:
                selected_grade = int(student_grade)
            elif selected_id.isdigit():
                selected_grade = int(selected_id)

            qs = ExtracurricularSchedule.objects.filter(is_active=True, when__gte=now).order_by("when", "id")

            if selected_grade:
                qs = qs.filter(grade=selected_grade)

            if q:
                qs = qs.filter(Q(title__icontains=q) | Q(place__icontains=q))

            paginator = Paginator(qs, self.paginate_by)
            page_number = (self.request.GET.get("page") or "1").strip()
            page_obj = paginator.get_page(page_number)

            params = self.request.GET.copy()
            params.pop("page", None)
            querystring = params.urlencode()

            context["schedules"] = list(page_obj.object_list)
            context["grades"] = [] if student_grade else grades
            context["selected_grade"] = selected_grade
            context["search_query"] = q
            context["page_obj"] = page_obj
            context["paginator"] = paginator
            context["is_paginated"] = page_has_other_pages(page_obj)
            context["total_schedules"] = paginator.count
            context["querystring"] = f"&{querystring}" if querystring else ""
        except (OperationalError, ProgrammingError):
            pass

        return context


class PortalParentsCommitteeView(LoginRequiredMixin, TemplateView):
    template_name = "secure/parents-committee.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["committee_page"] = None
        context["committee_focus_areas"] = []
        context["committee_members"] = []
        context["committee_meetings"] = []

        try:
            from site_content.models import ParentsCommitteePage

            now = timezone.now()
            page = ParentsCommitteePage.objects.first()
            context["committee_page"] = page
            if page:
                context["committee_focus_areas"] = list(
                    page.focus_areas.filter(is_active=True).order_by("order", "id")
                )
                context["committee_members"] = list(
                    page.members.filter(is_active=True).order_by("order", "id")
                )
                context["committee_meetings"] = list(
                    page.meetings.filter(is_active=True, start_at__gte=now).order_by("start_at", "id")
                )
        except (OperationalError, ProgrammingError):
            pass

        return context


class PortalTeachersCommitteeView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    template_name = "secure/teachers-committee.html"
    allowed_roles = {"teacher"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["committee_page"] = None
        context["committee_focus_areas"] = []
        context["committee_members"] = []
        context["committee_meetings"] = []

        try:
            from site_content.models import TeachersCommitteePage

            now = timezone.now()
            page = TeachersCommitteePage.objects.first()
            context["committee_page"] = page
            if page:
                context["committee_focus_areas"] = list(
                    page.focus_areas.filter(is_active=True).order_by("order", "id")
                )
                context["committee_members"] = list(
                    page.members.select_related("staff").filter(is_active=True).order_by("order", "id")
                )
                context["committee_meetings"] = list(
                    page.meetings.filter(is_active=True, start_at__gte=now).order_by("start_at", "id")
                )
        except (OperationalError, ProgrammingError):
            pass

        return context


class TeachersCommitteeView(TemplateView):
    template_name = "teachers-committee.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["committee_page"] = None
        context["committee_focus_areas"] = []
        context["committee_members"] = []
        context["committee_meetings"] = []

        try:
            from site_content.models import TeachersCommitteePage

            now = timezone.now()
            page = TeachersCommitteePage.objects.first()
            context["committee_page"] = page
            if page:
                context["committee_focus_areas"] = list(
                    page.focus_areas.filter(is_active=True).order_by("order", "id")
                )
                context["committee_members"] = list(
                    page.members.select_related("staff").filter(is_active=True).order_by("order", "id")
                )
                context["committee_meetings"] = list(
                    page.meetings.filter(is_active=True, start_at__gte=now).order_by("start_at", "id")
                )
        except (OperationalError, ProgrammingError):
            pass

        return context


class StudentsCommunityView(TemplateView):
    template_name = "students-community.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["community_page"] = None
        context["community_members"] = []

        try:
            from site_content.models import StudentsCommunityPage

            page = StudentsCommunityPage.objects.first()
            context["community_page"] = page
            if page:
                context["community_members"] = list(
                    page.members.select_related("student", "student__school_class")
                    .filter(is_active=True)
                    .order_by("order", "id")
                )
        except (OperationalError, ProgrammingError):
            pass

        return context


def handler404(request, exception):
    return render(request, "404.html", status=404)


def handler500(request):
    return render(request, "500.html", status=500)


class PortalMaterialManageView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    template_name = "secure/material-manage.html"
    allowed_roles = {"teacher"}

    paginate_by = 20

    def get_context_data(self, **kwargs):
        from django.urls import reverse

        context = super().get_context_data(**kwargs)

        context["active_tab"] = (self.request.GET.get("tab") or "plans").strip() or "plans"
        context["staff_profile"] = None
        context["plan_form"] = None
        context["plan_material_form"] = None
        context["assignment_form"] = None
        context["assignment_material_form"] = None
        context["uploads"] = []
        context["page_obj"] = None
        context["paginator"] = None
        context["is_paginated"] = False
        context["querystring"] = ""

        staff = _get_staff_profile(self.request)
        context["staff_profile"] = staff

        try:
            from academics.forms import (
                AssignmentMaterialCreateForm,
                ClassAssignmentCreateForm,
                LessonMaterialCreateForm,
                LessonPlanCreateForm,
            )

            context["plan_form"] = context.get("plan_form") or LessonPlanCreateForm(staff=staff)
            context["plan_material_form"] = context.get("plan_material_form") or LessonMaterialCreateForm(staff=staff)
            context["assignment_form"] = context.get("assignment_form") or ClassAssignmentCreateForm(staff=staff)
            context["assignment_material_form"] = context.get("assignment_material_form") or AssignmentMaterialCreateForm(
                staff=staff
            )
        except Exception:
            pass

        try:
            from academics.models import AssignmentMaterial, LessonMaterial

            lesson_qs = (
                LessonMaterial.objects.select_related("lesson_plan", "lesson_plan__subject")
                .filter(lesson_plan__teacher=staff)
                .order_by("-created_at", "-id")
            )
            assignment_qs = (
                AssignmentMaterial.objects.select_related("assignment", "assignment__subject")
                .filter(assignment__teacher=staff)
                .order_by("-created_at", "-id")
            )

            uploads = []
            for m in lesson_qs[:500]:
                plan = m.lesson_plan
                file_name = (m.file.name.rsplit("/", 1)[-1] if m.file else "") or "Link"
                uploads.append(
                    {
                        "kind": "Lesson material",
                        "subject": plan.subject,
                        "grade": plan.grade,
                        "created_at": m.created_at,
                        "file_name": file_name,
                        "icon": "description" if m.file else "link",
                        "admin_change_url": reverse("admin:academics_lessonmaterial_change", args=[m.pk]),
                        "admin_delete_url": reverse("admin:academics_lessonmaterial_delete", args=[m.pk]),
                    }
                )

            for m in assignment_qs[:500]:
                assignment = m.assignment
                file_name = (m.file.name.rsplit("/", 1)[-1] if m.file else "") or "Link"
                uploads.append(
                    {
                        "kind": "Extra task",
                        "subject": assignment.subject,
                        "grade": assignment.grade,
                        "created_at": m.created_at,
                        "file_name": file_name,
                        "icon": "description" if m.file else "link",
                        "admin_change_url": reverse("admin:academics_assignmentmaterial_change", args=[m.pk]),
                        "admin_delete_url": reverse("admin:academics_assignmentmaterial_delete", args=[m.pk]),
                    }
                )

            uploads.sort(key=lambda x: (x["created_at"] or timezone.now()), reverse=True)

            paginator = Paginator(uploads, self.paginate_by)
            page_number = (self.request.GET.get("page") or "1").strip()
            page_obj = paginator.get_page(page_number)

            params = self.request.GET.copy()
            params.pop("page", None)
            qs = params.urlencode()

            context["uploads"] = list(page_obj.object_list)
            context["page_obj"] = page_obj
            context["paginator"] = paginator
            context["is_paginated"] = page_has_other_pages(page_obj)
            context["querystring"] = f"&{qs}" if qs else ""
        except (OperationalError, ProgrammingError):
            pass

        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        from django.shortcuts import redirect
        from django.urls import reverse

        staff = _get_staff_profile(request)
        if not staff:
            return redirect(reverse("material-manage"))

        action = (request.POST.get("action") or "").strip()

        try:
            from academics.forms import (
                AssignmentMaterialCreateForm,
                ClassAssignmentCreateForm,
                LessonMaterialCreateForm,
                LessonPlanCreateForm,
            )
        except Exception:
            return redirect(reverse("material-manage"))

        if action == "create_plan":
            form = LessonPlanCreateForm(request.POST, staff=staff)
            if form.is_valid():
                form.save()
                return redirect(f"{reverse('material-manage')}?saved=plan&tab=plans")
            context = self.get_context_data(**kwargs)
            context["plan_form"] = form
            context["active_tab"] = "plans"
            return self.render_to_response(context)

        if action == "add_plan_material":
            form = LessonMaterialCreateForm(request.POST, request.FILES, staff=staff)
            if form.is_valid():
                form.save()
                return redirect(f"{reverse('material-manage')}?saved=plan_material&tab=plans")
            context = self.get_context_data(**kwargs)
            context["plan_material_form"] = form
            context["active_tab"] = "plans"
            return self.render_to_response(context)

        if action == "create_assignment":
            form = ClassAssignmentCreateForm(request.POST, staff=staff)
            if form.is_valid():
                form.save()
                return redirect(f"{reverse('material-manage')}?saved=assignment&tab=tasks")
            context = self.get_context_data(**kwargs)
            context["assignment_form"] = form
            context["active_tab"] = "tasks"
            return self.render_to_response(context)

        if action == "add_assignment_material":
            form = AssignmentMaterialCreateForm(request.POST, request.FILES, staff=staff)
            if form.is_valid():
                form.save()
                return redirect(f"{reverse('material-manage')}?saved=assignment_material&tab=tasks")
            context = self.get_context_data(**kwargs)
            context["assignment_material_form"] = form
            context["active_tab"] = "tasks"
            return self.render_to_response(context)

        return redirect(reverse("material-manage"))
