from django.urls import path

from .views import SiteLoginView, SiteLogoutView

urlpatterns = [
    path("login/", SiteLoginView.as_view(), name="login"),
    path("logout/", SiteLogoutView.as_view(), name="logout"),
]

