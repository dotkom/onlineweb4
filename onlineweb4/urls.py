from django.conf import settings
from django.conf.urls import include, re_path
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.views.generic import TemplateView
from django_js_reverse.views import urls_js

# URL config
admin.autodiscover()

urlpatterns = [
    # Admin urls
    re_path(r"^admin/doc/", include("django.contrib.admindocs.urls")),
    re_path(r"^admin/", admin.site.urls),
    # Onlineweb front page
    re_path(r"^$", TemplateView.as_view(template_name="frontpage.html"), name="home"),
    # Django-js-reverse used to get django urls to react
    re_path(r"^jsreverse/$", urls_js, name="js_reverse"),
    # nav-bar menu urls
    re_path(
        r"^#events$",
        TemplateView.as_view(template_name="frontpage.html"),
        name="events-link",
    ),
    re_path(
        r"^#articles$",
        TemplateView.as_view(template_name="frontpage.html"),
        name="articles-link",
    ),
    re_path(
        r"^#about$",
        TemplateView.as_view(template_name="frontpage.html"),
        name="about-link",
    ),
    re_path(
        r"^#business$",
        TemplateView.as_view(template_name="frontpage.html"),
        name="business-link",
    ),
    re_path(
        r"^#offline$",
        TemplateView.as_view(template_name="frontpage.html"),
        name="offline-link",
    ),
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
    re_path(r"^wiki/", include("wiki.urls")),
]


# Onlineweb app urls
if "apps.api" in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r"^api/", include("apps.api.urls"))]

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

if "apps.autoconfig" in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r"^mail/", include("apps.autoconfig.urls"))]

if "apps.authentication" in settings.INSTALLED_APPS:
    urlpatterns += [
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

if "apps.contact" in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r"^contact/", include("apps.contact.urls"))]

if "apps.contribution" in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r"^contribution/", include("apps.contribution.urls"))]

if "apps.dashboard" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^dashboard/", include("apps.dashboard.urls")),
        re_path(
            r"^dashboard/chunks/",
            include(
                "apps.dashboard.chunks.dashboard.urls", namespace="chunk-dashboard"
            ),
        ),
    ]

if "apps.dataporten" in settings.INSTALLED_APPS:
    from apps.dataporten import urls as dataporten_urls

    urlpatterns += [
        re_path(r"^dataporten/", include(dataporten_urls, namespace="dataporten"))
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
        re_path(r"^dashboard/marks/", include("apps.marks.dashboard.urls")),
    ]

if "apps.notifications" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^notifications/", include("apps.notifications.urls")),
    ]

if "apps.online_oidc_provider" in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r"^oidc/", include("apps.online_oidc_provider.urls"))]

if "apps.inventory" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^dashboard/inventory/", include("apps.inventory.dashboard.urls"))
    ]

if "apps.shop" in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r"^shop/", include("apps.shop.urls"))]

if "apps.offline" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^offline/", include("apps.offline.urls")),
    ]

if "apps.posters" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^dashboard/posters/", include("apps.posters.dashboard.urls"))
    ]

if "apps.profiles" in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r"^profile/", include("apps.profiles.urls"))]

if "apps.photoalbum" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^photoalbum/", include("apps.photoalbum.urls")),
        re_path(
            r"^dashboard/photoalbum/",
            include("apps.photoalbum.dashboard.urls", namespace="dashboard-photoalbum"),
        ),
    ]

if (
    "apps.resourcecenter" in settings.INSTALLED_APPS
    and "apps.mailinglists" in settings.INSTALLED_APPS
):
    urlpatterns += [
        re_path(
            r"^resourcecenter/mailinglists/", include("apps.mailinglists.urls")
        ),  # leave in this order because...
        re_path(
            r"^resourcecenter/", include("apps.resourcecenter.urls")
        ),  # Resourcecenter has catch-all on subpages
        re_path(
            r"^dashboard/resources/", include("apps.resourcecenter.dashboard.urls")
        ),
    ]

if "apps.slack" in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r"^slack/", include("apps.slack.urls"))]

if "apps.splash" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^splash/", include("apps.splash.urls")),
        re_path(r"^splash/", include("apps.splash.api.urls")),
    ]

if "apps.sso" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^sso/", include("apps.sso.urls")),
        re_path(
            r"^sso/", include("oauth2_provider.urls", namespace="oauth2_provider")
        ),  # Shadow URL path to allow overrides in apps.sso.urls.
        re_path(
            r"^dashboard/auth/sso/",
            include("apps.sso.dashboard.urls", namespace="dashboard"),
        ),
    ]

if "apps.webshop" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^webshop/", include("apps.webshop.urls")),
        re_path(
            r"^dashboard/webshop/",
            include("apps.webshop.dashboard.urls", namespace="dashboard-webshop"),
        ),
    ]

if "apps.chunksapi" in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r"^chunks/", include("apps.chunksapi.urls"))]

if "apps.payment" in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r"^payment/", include("apps.payment.urls"))]

# redwine
if "redwine" in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r"^redwine/", include("redwine.urls"))]

if "rest_framework" in settings.INSTALLED_APPS:
    from apps.api.utils import SharedAPIRootRouter

    urlpatterns += [
        re_path(r"^api/v1/", include(SharedAPIRootRouter.shared_router.urls))
    ]

if "oidc_provider" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^openid/", include("oidc_provider.urls", namespace="oidc_provider"))
    ]

# http://docs.djangoproject.com/en/1.3/howto/static-files/#staticfiles-development
if settings.DEBUG:
    # Media
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler500 = "onlineweb4.views.handler500"
