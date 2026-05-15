from __future__ import annotations

from django.test import TestCase
from django.urls import reverse


class GalleryPageSmokeTests(TestCase):
    def test_gallery_page_renders(self) -> None:
        response = self.client.get(reverse("gallery"))
        self.assertEqual(response.status_code, 200)

    def test_gallery_page_invalid_page_param_renders(self) -> None:
        response = self.client.get(reverse("gallery"), {"page": "not-a-number"})
        self.assertEqual(response.status_code, 200)

    def test_gallery_page_out_of_range_page_param_renders(self) -> None:
        response = self.client.get(reverse("gallery"), {"page": "999999"})
        self.assertEqual(response.status_code, 200)
