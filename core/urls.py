from django.urls import include, path

from clubs.views import ClubDetailView, ClubListView
from competitions.views import AchievementsListView
from events_extracurricular.views import ExtracurricularEventDetailView, ExtracurricularEventListView
from events_school.views import SchoolEventDetailView, SchoolEventListView, school_event_type_posts
from news.views import NewsDetailView, NewsListView
from people.api import graduate_destinations
from perspective.views import ConstructionPostDetailView, PerspectivePageView

from .views import (
    AboutPageView,
    AdmissionsPageView,
    ContactPageView,
    EmployeesPageView,
    GalleryPageView,
    MethodicalMaterialsPageView,
    PortalExtracurricularSchedulesView,
    PortalMaterialManageView,
    PortalParentsCommitteeView,
    PortalTeachersCommitteeView,
    PortalPlansView,
    PortalResourcesView,
    PublicPageView,
    SchedulesPageView,
    StudentsCommunityView,
    TeachersCommitteeView,
)

urlpatterns = [
    path("", include("accounts.urls")),
    path("", PublicPageView.as_view(template_name="index.html"), name="index"),
    path("about/", AboutPageView.as_view(), name="about"),
    path("achievements/", AchievementsListView.as_view(), name="achievments"),
    path("admissions/", AdmissionsPageView.as_view(), name="admissions"),
    path("clubs/", ClubListView.as_view(), name="clubs"),
    path("clubs/<slug:slug>/", ClubDetailView.as_view(), name="club-detail"),
    path("contact/", ContactPageView.as_view(), name="contact"),
    path("employees/", EmployeesPageView.as_view(), name="employees"),
    path("gallery/", GalleryPageView.as_view(), name="gallery"),
    path("methodical-materials/", MethodicalMaterialsPageView.as_view(), name="methodical-materials"),
    path("perspective/", PerspectivePageView.as_view(), name="perspective"),
    path("perspective/construction/<slug:slug>/", ConstructionPostDetailView.as_view(), name="perspective-construction"),
    path("news/", NewsListView.as_view(), name="news"),
    path("news/<slug:slug>/", NewsDetailView.as_view(), name="news-detail"),
    path("schedules/", SchedulesPageView.as_view(), name="schedules"),
    path("students-community/", StudentsCommunityView.as_view(), name="students-community"),
    path("teachers-committee/", TeachersCommitteeView.as_view(), name="teachers-committee-public"),
    path("activities/<slug:type_key>/", school_event_type_posts, name="activity-overview"),
    path("events/school/", SchoolEventListView.as_view(), name="school-events"),
    path("events/school/<int:pk>/", SchoolEventDetailView.as_view(), name="school-event-detail"),
    path("events/extracurricular/", ExtracurricularEventListView.as_view(), name="extracurricular-events"),
    path(
        "events/extracurricular/<int:pk>/",
        ExtracurricularEventDetailView.as_view(),
        name="extracurricular-event-detail",
    ),
    path(
        "events/<slug:slug>/",
        PublicPageView.as_view(template_name="event-detail.html"),
        name="event-detail",
    ),
    path("teachers-committee/", PortalTeachersCommitteeView.as_view(), name="teachers-committee"),
    path("portal/resources/", PortalResourcesView.as_view(), name="resources"),
    path("portal/plans/", PortalPlansView.as_view(), name="plans"),
    path("portal/material-manage/", PortalMaterialManageView.as_view(), name="material-manage"),
    path("portal/parents-committee/", PortalParentsCommitteeView.as_view(), name="parents-committee"),
    path(
        "portal/extracurricular-schedules/",
        PortalExtracurricularSchedulesView.as_view(),
        name="extracurricular-schedules",
    ),
    path("api/graduates/destinations/", graduate_destinations, name="api-graduate-destinations"),
]
