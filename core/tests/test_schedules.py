from __future__ import annotations

import datetime as dt

from django.test import TestCase
from django.urls import reverse
from django.utils import translation


class SchedulesPageTests(TestCase):
    def test_schedules_page_renders_without_data(self) -> None:
        response = self.client.get(reverse("schedules"))
        self.assertEqual(response.status_code, 200)

    def test_schedules_page_weekdays_translated(self) -> None:
        from academics.models import ClassLesson, TimeSlot
        from people.models import SchoolClass, Subject

        school_class = SchoolClass.objects.create(name="A", grade=2, is_active=True)
        subject = Subject.objects.create(name="Math")
        slot = TimeSlot.objects.create(number=1, start_time=dt.time(9, 0), end_time=dt.time(9, 45))
        ClassLesson.objects.create(
            school_class=school_class,
            weekday=1,
            slot=slot,
            subject=subject,
            is_public=True,
        )

        with translation.override("ru"):
            response = self.client.get(reverse("schedules"), {"grade": "2"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Понедельник")

    def test_schedules_page_filters_by_grade(self) -> None:
        from academics.models import TimeSlot
        from people.models import SchoolClass

        TimeSlot.objects.create(number=1, start_time=dt.time(9, 0), end_time=dt.time(9, 45))
        c2a = SchoolClass.objects.create(name="A", grade=2, is_active=True)
        c3a = SchoolClass.objects.create(name="A", grade=3, is_active=True)

        response = self.client.get(reverse("schedules"), {"grade": "2"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, c2a.display_name)
        self.assertNotContains(response, c3a.display_name)
