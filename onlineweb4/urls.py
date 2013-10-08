from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.http import HttpResponse
from django.views.generic import TemplateView

from apps import mommy

from filebrowser.sites import site

# URL config
admin.autodiscover()

# Mommy config
mommy.autodiscover()
mommy.run()

urlpatterns = patterns('',
    # Filebrowser must be above all admin-urls
    url(r'^admin/filebrowser/',     include(site.urls)),
    url(r'^grappelli/',             include('grappelli.urls')),

    # Admin urls
    url(r'^admin/',             include(admin.site.urls)),
    url(r'^admin/doc/',         include('django.contrib.admindocs.urls')),

    # Onlineweb app urls
    url(r'^$', TemplateView.as_view(template_name='frontpage.html'), name='home'),
    url(r'^api/',               include('apps.api.urls')),
    url(r'^article/',           include('apps.article.urls')),
    url(r'^careeropportunity/', include('apps.careeropportunity.urls')),
    url(r'^company/',           include('apps.companyprofile.urls')),
    url(r'^events/',            include('apps.events.urls')),
    url(r'^mail/',              include('apps.autoconfig.urls')),
    url(r'^auth/',              include('apps.authentication.urls')),
    url(r'^feedback/',          include('apps.feedback.urls')),
    url(r'^offline/',           include('apps.offline.urls')),
    url(r'^profile/',           include('apps.profiles.urls')),
    url(r'^resourcecenter/mailinglists/', include('apps.mailinglists.urls')), # leave in this order because...
    url(r'^resourcecenter/',    include('apps.resourcecenter.urls')), # ...resourcecenter has catch-all on subpages

    # nav-bar menu urls
    url(r'^#events$', TemplateView.as_view(template_name='frontpage.html#events'), name='events-link'),
    url(r'^#articles$', TemplateView.as_view(template_name='frontpage.html#articles'), name='articles-link'),
    url(r'^#about$', TemplateView.as_view(template_name='frontpage.html#about'), name='about-link'),
    url(r'^#business$', TemplateView.as_view(template_name='frontpage.html#business'), name='business-link'),
    url(r'^#offline$', TemplateView.as_view(template_name='frontpage.html#offline'), name='offline-link'),

    # Online Notifier Owner Verification (checked yearly or so by Google)
    url(r'^google79c0b331a83a53de\.html$', lambda r: HttpResponse(
        "google-site-verification: google79c0b331a83a53de.html", mimetype="text/html")),
)
# pizzasystem
if 'pizzasystem' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', url(r'^pizza/', include('pizzasystem.urls')))

#Captcha url
if 'captcha' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', url(r'^captcha/', include('captcha.urls')))



# http://docs.djangoproject.com/en/1.3/howto/static-files/#staticfiles-development
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
            'show_indexes': True
        }),
        (r'^500/$', 'django.views.defaults.server_error'),
    )
