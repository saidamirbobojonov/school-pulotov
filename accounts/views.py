from django.contrib.auth.views import LoginView, LogoutView
from django.db.utils import OperationalError, ProgrammingError

from .forms import PortalAuthenticationForm


class SiteLoginView(LoginView):
    template_name = "login.html"
    authentication_form = PortalAuthenticationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        grades = []
        try:
            from people.models import SchoolClass

            grades = list(
                SchoolClass.objects.filter(is_active=True)
                .values_list("grade", flat=True)
                .distinct()
                .order_by("grade")
            )
        except (ImportError, OperationalError, ProgrammingError):
            grades = []

        context["grades"] = grades or list(range(1, 12))
        return context

    def get_success_url(self):
        return super().get_success_url()


class SiteLogoutView(LogoutView):
    pass
