from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django_js_reverse.views import urls_js
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# URL config
admin.autodiscover()


class HomePageView(TemplateView):
    template_name = "frontpage.html"


def redirect_to_new_wiki(request, path):
    return redirect(f"https://wiki.online.ntnu.no/{path}", permanent=True)


urlpatterns = [
    # Admin urls
    re_path(r"^admin/doc/", include("django.contrib.admindocs.urls")),
    re_path(r"^admin/", admin.site.urls),
    # Onlineweb front page
    re_path(r"^$", HomePageView.as_view(), name="home"),
    # Django-js-reverse used to get django urls to react
    re_path(r"^jsreverse/$", urls_js, name="js_reverse"),
    # Online Notifier Owner Verification (checked yearly or so by Google)
    re_path(
        r"^google79c0b331a83a53de\.html$",
        lambda r: HttpResponse(
            "google-site-verification: google79c0b331a83a53de.html",
            content_type="text/html",
        ),
    ),
    # Wiki
    re_path(r"^notify/", include("django_nyt.urls")),
    re_path(r"^wiki/online/(?!komiteer/)(?P<path>([^/]+/)*)$", redirect_to_new_wiki),
    re_path(r"^wiki/$", lambda r: redirect_to_new_wiki(r, "")),
    re_path(r"^wiki/", include("wiki.urls")),
]

# Robots.txt
urlpatterns += [
    re_path(r"^robots.txt$", TemplateView.as_view(template_name="robots.txt", content_type="text/plain"))
]

# Onlineweb app urls

if "apps.approval" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^approval/", include("apps.approval.urls")),
        re_path(r"^dashboard/approval/", include("apps.approval.dashboard.urls")),
        re_path(r"^committeeapplication/", include("apps.approval.api.urls")),
    ]

if "apps.article" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^article/", include("apps.article.urls")),
        re_path(r"^dashboard/article/", include("apps.article.dashboard.urls")),
    ]

if "apps.authentication" in settings.INSTALLED_APPS:
    urlpatterns += [
        # our config is kinda wack for API-s, this is only here to import the file that sets stuff for SharedAPIRouter
        re_path(r"^auth/", include("apps.authentication.urls")),
        re_path(r"^dashboard/auth/", include("apps.authentication.dashboard.urls")),
    ]

if "apps.careeropportunity" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^careeropportunity/", include("apps.careeropportunity.urls")),
        re_path(
            r"^dashboard/careeropportunity/",
            include("apps.careeropportunity.dashboard.urls"),
        ),
    ]

if "apps.companyprofile" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^company/", include("apps.companyprofile.urls")),
        re_path(r"^dashboard/company/", include("apps.companyprofile.dashboard.urls")),
    ]

if "apps.dashboard" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^dashboard/", include("apps.dashboard.urls")),
    ]

if "apps.dataporten" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(
            r"^dataporten/", include("apps.dataporten.urls", namespace="dataporten")
        )
    ]

if "apps.events" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^events/", include("apps.events.urls")),
        re_path(r"^dashboard/events/", include("apps.events.dashboard.urls")),
        re_path(
            r"^events-api/", include("apps.events.api.urls")
        ),  # url is a dummy, but needed to import the file
    ]

if "apps.feedback" in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r"^feedback/", include("apps.feedback.urls"))]

if "apps.gallery" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^gallery/", include("apps.gallery.urls", namespace="gallery")),
        re_path(
            r"^dashboard/gallery/",
            include("apps.gallery.dashboard.urls", namespace="gallery_dashboard"),
        ),
    ]

if "apps.hobbygroups" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^hobbygroups/", include("apps.hobbygroups.urls")),
        re_path(r"^dashboard/hobbies/", include("apps.hobbygroups.dashboard.urls")),
    ]

if "apps.marks" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^marks/", include("apps.marks.urls")),
    ]

if "apps.notifications" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^notifications/", include("apps.notifications.urls")),
    ]

if "apps.posters" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^dashboard/posters/", include("apps.posters.dashboard.urls"))
    ]

if "apps.profiles" in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r"^profile/", include("apps.profiles.urls"))]

urlpatterns += [
    re_path(
        r"^resourcecenter/mailinglists/$",
        lambda _request: redirect(
            "https://wiki.online.ntnu.no/linjeforening/e-postlister/",
            permanent=True,
        ),
    ),
]

if "apps.splash" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^splash/", include("apps.splash.urls")),
        re_path(r"^splash/", include("apps.splash.api.urls")),
    ]

if "apps.webshop" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^webshop/", include("apps.webshop.urls")),
        re_path(
            r"^dashboard/webshop/",
            include("apps.webshop.dashboard.urls", namespace="dashboard-webshop"),
        ),
    ]

if "apps.payment" in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r"^payment/", include("apps.payment.urls"))]

if "rest_framework" in settings.INSTALLED_APPS:
    from apps.api.utils import SharedAPIRootRouter

    urlpatterns += [
        re_path(r"^api/v1/", include(SharedAPIRootRouter.shared_router.urls)),
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "api/schema/swagger-ui/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path(
            "api/schema/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
    ]

if "mozilla_django_oidc" in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r"^auth0/", include("mozilla_django_oidc.urls"))]

# http://docs.djangoproject.com/en/1.3/howto/static-files/#staticfiles-development
if settings.DEBUG:
    # Media
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler500 = "onlineweb4.views.handler500"
