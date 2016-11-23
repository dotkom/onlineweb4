from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.views.defaults import server_error
from django.views.generic import TemplateView
from django_js_reverse.views import urls_js
from django_nyt.urls import get_pattern as get_notify_pattern
from filebrowser.sites import site
from wiki.urls import get_pattern as get_wiki_pattern
from onlineweb4 import views

# URL config
admin.autodiscover()

urlpatterns = [
    # Filebrowser must be above all admin-urls
    url(r'^admin/filebrowser/',     include(site.urls)),
    url(r'^grappelli/',             include('grappelli.urls')),

    # Admin urls
    url(r'^admin/',             include(admin.site.urls)),
    url(r'^admin/doc/',         include('django.contrib.admindocs.urls')),

    # Onlineweb front page
    url(r'^$', TemplateView.as_view(template_name='frontpage.html'), name='home'),

    # Django-js-reverse used to get django urls to react
    url(r'^jsreverse/$', urls_js, name='js_reverse'),

    # nav-bar menu urls
    url(r'^#events$', TemplateView.as_view(template_name='frontpage.html'), name='events-link'),
    url(r'^#articles$', TemplateView.as_view(template_name='frontpage.html'), name='articles-link'),
    url(r'^#about$', TemplateView.as_view(template_name='frontpage.html'), name='about-link'),
    url(r'^#business$', TemplateView.as_view(template_name='frontpage.html'), name='business-link'),
    url(r'^#offline$', TemplateView.as_view(template_name='frontpage.html'), name='offline-link'),

    # Online Notifier Owner Verification (checked yearly or so by Google)
    url(r'^google79c0b331a83a53de\.html$', lambda r: HttpResponse(
        "google-site-verification: google79c0b331a83a53de.html", content_type="text/html")),

    # Wiki
    url(r'^notify/', get_notify_pattern()),
    url(r'^wiki/', get_wiki_pattern())
]


# Onlineweb app urls
if 'apps.api' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^api/',               include('apps.api.urls')),
    ]

if 'apps.approval' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^approval/',              include('apps.approval.urls')),
        url(r'^dashboard/approval/',    include('apps.approval.dashboard.urls')),
    ]

if 'apps.article' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^article/',           include('apps.article.urls')),
        url(r'^dashboard/article/', include('apps.article.dashboard.urls')),
    ]

if 'apps.autoconfig' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^mail/',              include('apps.autoconfig.urls')),
    ]

if 'apps.authentication' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^auth/',              include('apps.authentication.urls')),
        url(r'^dashboard/auth/',    include('apps.authentication.dashboard.urls')),
    ]

if 'apps.careeropportunity' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^careeropportunity/', include('apps.careeropportunity.urls')),
        url(r'^dashboard/careeropportunity/', include('apps.careeropportunity.dashboard.urls')),
    ]

if 'apps.companyprofile' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^company/',           include('apps.companyprofile.urls')),
        url(r'^dashboard/company/', include('apps.companyprofile.dashboard.urls')),
    ]

if 'apps.dashboard' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^dashboard/',         include('apps.dashboard.urls')),
        url(r'^dashboard/chunks/', include('apps.dashboard.chunks.dashboard.urls', namespace='chunk-dashboard')),
    ]

if 'apps.events' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^events/',            include('apps.events.urls')),
        url(r'^dashboard/events/',  include('apps.events.dashboard.urls')),
    ]

if 'apps.feedback' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^feedback/',          include('apps.feedback.urls')),
    ]

if 'apps.gallery' in settings.INSTALLED_APPS:
    urlpatterns += [
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
    ]

if 'apps.genfors' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^genfors/',           include('apps.genfors.urls')),
    ]

if 'apps.marks' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^dashboard/marks/',          include('apps.marks.dashboard.urls')),
    ]

if 'apps.inventory' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^dashboard/inventory/',          include('apps.inventory.dashboard.urls')),
    ]

if 'apps.shop' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^shop/',          include('apps.shop.urls')),
    ]

if 'apps.offline' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^offline/',           include('apps.offline.urls')),
    ]

if 'apps.posters' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^dashboard/posters/',          include('apps.posters.dashboard.urls')),
    ]

if 'apps.profiles' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^profile/',           include('apps.profiles.urls')),
    ]

if 'apps.resourcecenter' in settings.INSTALLED_APPS and 'apps.mailinglists' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^resourcecenter/mailinglists/', include('apps.mailinglists.urls')),  # leave in this order because...
        url(r'^resourcecenter/',    include('apps.resourcecenter.urls')),  # Resourcecenter has catch-all on subpages
    ]

if 'apps.rutinator' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^dashboard/rutinator/', include(
            'apps.rutinator.dashboard.urls',
            namespace='dashboard',
            app_name='rutinator'
        )),
    ]

if 'apps.slack' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^slack/', include('apps.slack.urls'))
    ]

if 'apps.splash' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^splash/',           include('apps.splash.urls')),
        url(r'^splash/',           include('apps.splash.api.urls')),
    ]

if 'apps.sso' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^sso/', include('apps.sso.urls')),
        url(r'^dashboard/auth/sso/', include('apps.sso.dashboard.urls', namespace='dashboard', app_name='sso')),
    ]

if 'apps.webshop' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^webshop/',           include('apps.webshop.urls')),
        url(r'^dashboard/webshop/', include(
            'apps.webshop.dashboard.urls',
            namespace='dashboard-webshop',
            app_name='webshop'
        )),
    ]

# feedme
if 'feedme' in settings.INSTALLED_APPS:
    feedme_urls = [
        url(r'^feedme/', include('feedme.urls', namespace='feedme')),
        url(r'^feedme-api/', include('feedme.api.urls', namespace='feedmeapi')),
        url(r'^feedme-react/', include('feedme.react.urls', namespace='feedmereact'))
    ]
    urlpatterns += feedme_urls

if 'apps.payment' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^payment/',           include('apps.payment.urls')),
    ]

# redwine
if 'redwine' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^redwine/', include('redwine.urls'))
    ]

if 'rest_framework' in settings.INSTALLED_APPS:
    from apps.api.utils import SharedAPIRootRouter

    # API
    def api_urls():
        return SharedAPIRootRouter.shared_router.urls

    urlpatterns += [
        url(r'^api/v1/', include(api_urls()))
    ]

#500 view
handler500 = views.server_error

# http://docs.djangoproject.com/en/1.3/howto/static-files/#staticfiles-development
if settings.DEBUG:
    # Media
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # 500
    urlpatterns += [
        url(r'^500/$', views.server_error),
    ]
