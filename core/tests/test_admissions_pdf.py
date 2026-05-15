from __future__ import annotations

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse


class AdmissionsPdfPreviewTests(TestCase):
    def test_admissions_page_renders_without_pdf(self) -> None:
        response = self.client.get(reverse("admissions"))
        self.assertEqual(response.status_code, 200)

    def test_admissions_page_shows_pdf_preview_button_when_pdf_present(self) -> None:
        from site_content.models import AdmissionsPage

        AdmissionsPage.objects.create(
            application_pdf=SimpleUploadedFile(
                "regulations.pdf",
                b"%PDF-1.4\n%Fake\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n",
                content_type="application/pdf",
            )
        )

        response = self.client.get(reverse("admissions"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "data-admissions-pdf-open")
        self.assertContains(response, "data-admissions-pdf-modal")
        self.assertContains(response, "#zoom=100")
