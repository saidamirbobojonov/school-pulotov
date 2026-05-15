from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.views import serve as staticfiles_serve
from django.urls import include, path
from django.views.i18n import set_language

urlpatterns = [
    path("set-language/", set_language, name="set_language"),
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
]

handler404 = "core.views.handler404"
handler500 = "core.views.handler500"

if settings.DEBUG or getattr(settings, "SERVE_STATICFILES", False):
    urlpatterns += static(settings.STATIC_URL, view=staticfiles_serve, kwargs={"insecure": True})
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
