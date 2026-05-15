from __future__ import annotations

from django.db.models import Count, F, Q
from django.utils import timezone
from django.views.generic import DetailView, ListView

from core.pagination import page_has_other_pages

from .models import NewsPost


class NewsListView(ListView):
    template_name = "news.html"
    context_object_name = "posts"
    paginate_by = 9

    featured_post: NewsPost | None = None

    def paginate_queryset(self, queryset, page_size):
        paginator = self.get_paginator(
            queryset,
            page_size,
            orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty(),
        )
        page_kwarg = self.page_kwarg
        page_number = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        page_obj = paginator.get_page(page_number)

        return paginator, page_obj, page_obj.object_list, page_has_other_pages(page_obj)

    def get_queryset(self):
        now = timezone.now()
        queryset = NewsPost.objects.filter(published_at__lte=now).order_by("-published_at", "-id")

        category = (self.request.GET.get("category") or "").strip()
        if category:
            queryset = queryset.filter(category=category)

        year = (self.request.GET.get("year") or "").strip()
        if year.isdigit():
            queryset = queryset.filter(published_at__year=int(year))

        query = ((self.request.GET.get("q") or "").strip())[:100]
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(body__icontains=query))

        page = (self.request.GET.get("page") or "1").strip()
        if page == "1":
            self.featured_post = queryset.first()
            if self.featured_post:
                queryset = queryset.exclude(pk=self.featured_post.pk)
        else:
            self.featured_post = None

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        now = timezone.now()
        category_choices = dict(NewsPost.CATEGORY_CHOICES)
        categories = list(
            NewsPost.objects.filter(published_at__lte=now)
            .values("category")
            .annotate(count=Count("id"))
            .order_by("category")
        )
        for item in categories:
            item["label"] = category_choices.get(item["category"], item["category"])

        years = [d.year for d in NewsPost.objects.filter(published_at__lte=now).dates("published_at", "year", order="DESC")]

        params = self.request.GET.copy()
        params.pop("page", None)
        querystring = params.urlencode()

        context["featured_post"] = self.featured_post
        context["categories"] = categories
        context["years"] = years
        context["active_category"] = (self.request.GET.get("category") or "").strip()
        context["active_year"] = (self.request.GET.get("year") or "").strip()
        context["search_query"] = ((self.request.GET.get("q") or "").strip())[:100]
        context["querystring"] = f"&{querystring}" if querystring else ""

        return context


class NewsDetailView(DetailView):
    template_name = "news-detail.html"
    context_object_name = "post"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        now = timezone.now()
        return (
            NewsPost.objects.filter(published_at__lte=now)
            .prefetch_related("gallery")
            .order_by("-published_at", "-id")
        )

    def get_object(self, queryset=None):
        obj: NewsPost = super().get_object(queryset=queryset)
        NewsPost.objects.filter(pk=obj.pk).update(views=F("views") + 1)
        obj.refresh_from_db(fields=["views"])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        now = timezone.now()
        post: NewsPost = context["post"]

        context["gallery_images"] = [item for item in post.gallery.all() if item.image]
        context["more_posts"] = list(
            NewsPost.objects.filter(published_at__lte=now)
            .exclude(pk=post.pk)
            .order_by("-published_at", "-id")[:3]
        )

        return context
