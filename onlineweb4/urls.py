from apps import mommy
from django.conf import settings
from django.conf.urls import include, patterns, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponse
from django.views.generic import TemplateView
from django_nyt.urls import get_pattern as get_notify_pattern
from filebrowser.sites import site
from wiki.urls import get_pattern as get_wiki_pattern

# URL config
admin.autodiscover()

urlpatterns = patterns(
    '',
    # Filebrowser must be above all admin-urls
    url(r'^admin/filebrowser/',     include(site.urls)),
    url(r'^grappelli/',             include('grappelli.urls')),

    # Admin urls
    url(r'^admin/',             include(admin.site.urls)),
    url(r'^admin/doc/',         include('django.contrib.admindocs.urls')),

    # Onlineweb front page
    url(r'^$', TemplateView.as_view(template_name='frontpage.html'), name='home'),

    # nav-bar menu urls
    url(r'^#events$', TemplateView.as_view(template_name='frontpage.html#events'), name='events-link'),
    url(r'^#articles$', TemplateView.as_view(template_name='frontpage.html#articles'), name='articles-link'),
    url(r'^#about$', TemplateView.as_view(template_name='frontpage.html#about'), name='about-link'),
    url(r'^#business$', TemplateView.as_view(template_name='frontpage.html#business'), name='business-link'),
    url(r'^#offline$', TemplateView.as_view(template_name='frontpage.html#offline'), name='offline-link'),

    # Online Notifier Owner Verification (checked yearly or so by Google)
    url(r'^google79c0b331a83a53de\.html$', lambda r: HttpResponse(
        "google-site-verification: google79c0b331a83a53de.html", content_type="text/html")),

    # Wiki
    (r'^notify/', get_notify_pattern()),
    (r'^wiki/', get_wiki_pattern())
)


# Onlineweb app urls
if 'apps.api' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url(r'^api/',               include('apps.api.urls')),
    )

if 'apps.approval' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url(r'^approval/',              include('apps.approval.urls')),
        url(r'^dashboard/approval/',    include('apps.approval.dashboard.urls')),
    )

if 'apps.article' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url(r'^article/',           include('apps.article.urls')),
        url(r'^dashboard/article/', include('apps.article.dashboard.urls')),
    )

if 'apps.autoconfig' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url(r'^mail/',              include('apps.autoconfig.urls')),
    )

if 'apps.authentication' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url(r'^auth/',              include('apps.authentication.urls')),
        url(r'^dashboard/auth/',    include('apps.authentication.dashboard.urls')),
    )

if 'apps.careeropportunity' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url(r'^careeropportunity/', include('apps.careeropportunity.urls')),
        url(r'^dashboard/careeropportunity/', include('apps.careeropportunity.dashboard.urls')),
    )

if 'apps.companyprofile' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url(r'^company/',           include('apps.companyprofile.urls')),
        url(r'^dashboard/company/', include('apps.companyprofile.dashboard.urls')),
    )

if 'apps.dashboard' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url(r'^dashboard/',         include('apps.dashboard.urls')),
    )

if 'apps.events' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url(r'^events/',            include('apps.events.urls')),
        url(r'^dashboard/events/',  include('apps.events.dashboard.urls')),
    )

if 'apps.feedback' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url(r'^feedback/',          include('apps.feedback.urls')),
    )

if 'apps.marks' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url(r'^dashboard/marks/',          include('apps.marks.dashboard.urls')),
    )

if 'apps.inventory' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url(r'^dashboard/inventory/',          include('apps.inventory.dashboard.urls')),
    )

if 'apps.offline' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url(r'^offline/',           include('apps.offline.urls')),
    )

if 'apps.posters' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url(r'^dashboard/posters/',          include('apps.posters.dashboard.urls')),
    )

if 'apps.profiles' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url(r'^profile/',           include('apps.profiles.urls')),
    )

if 'apps.resourcecenter' in settings.INSTALLED_APPS and 'apps.mailinglists' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url(r'^resourcecenter/mailinglists/', include('apps.mailinglists.urls')),  # leave in this order because...
        url(r'^resourcecenter/',    include('apps.resourcecenter.urls')),  # Resourcecenter has catch-all on subpages
    )

if 'apps.genfors' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url(r'^genfors/',           include('apps.genfors.urls')),
    )


if 'apps.gallery' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url(
            r'^gallery/',
            include(
                'apps.gallery.urls',
                namespace='gallery',
                app_name='gallery'
            )
        ),
        url(
            r'^dashboard/gallery/',
            include(
                'apps.gallery.dashboard.urls',
                namespace='gallery_dashboard',
                app_name='gallery'
            )
        )
    )

if 'apps.splash' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url(r'^splash/',           include('apps.splash.urls')),
    )

if 'apps.sso' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url(r'^sso/', include('apps.sso.urls')),
        url(r'^dashboard/auth/sso/', include('apps.sso.dashboard.urls', namespace='dashboard', app_name='sso')),
    )

# feedme
if 'feedme' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', url(r'^feedme/', include('feedme.urls', namespace='feedme')))

if 'apps.payment' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url(r'^payment/',           include('apps.payment.urls')),
    )

# redwine
if 'redwine' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', url(r'^redwine/', include('redwine.urls')))

if 'rest_framework' in settings.INSTALLED_APPS:
    from apps.api.utils import SharedAPIRootRouter

    # API
    def api_urls():
        return SharedAPIRootRouter.shared_router.urls

    urlpatterns += patterns(
        '',
        url(r'^api/v1/', include(api_urls())),
    )


# http://docs.djangoproject.com/en/1.3/howto/static-files/#staticfiles-development
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

    urlpatterns += patterns(
        '',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
            'show_indexes': True
        }),
        (r'^500/$', 'django.views.defaults.server_error'),
    )
