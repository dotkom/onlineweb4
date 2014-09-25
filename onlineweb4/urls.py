from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.http import HttpResponse
from django.views.generic import TemplateView
from django_notify.urls import get_pattern as get_notify_pattern

from wiki.urls import get_pattern as get_wiki_pattern
from filebrowser.sites import site

from apps import mommy

# URL config
admin.autodiscover()

urlpatterns = patterns('',
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
        "google-site-verification: google79c0b331a83a53de.html", mimetype="text/html")),
    
    # Wiki
    (r'^notify/', get_notify_pattern()),
    (r'^wiki/', get_wiki_pattern())
)


# Onlineweb app urls
if 'apps.api' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^api/',               include('apps.api.urls')),
    )

if 'apps.article' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^article/',           include('apps.article.urls')),
    )

if 'apps.careeropportunity' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^careeropportunity/', include('apps.careeropportunity.urls')),
    )

if 'apps.companyprofile' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^company/',           include('apps.companyprofile.urls')),
    )

if 'apps.events' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^events/',            include('apps.events.urls')),
    )

if 'apps.autoconfig' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^mail/',              include('apps.autoconfig.urls')),
    )

if 'apps.authentication' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^auth/',              include('apps.authentication.urls')),
    )

if 'apps.feedback' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^feedback/',          include('apps.feedback.urls')),
    )

if 'apps.offline' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^offline/',           include('apps.offline.urls')),
    )

if 'apps.profiles' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^profile/',           include('apps.profiles.urls')),
    )

if 'apps.resourcecenter' in settings.INSTALLED_APPS and 'apps.mailinglists' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^resourcecenter/mailinglists/', include('apps.mailinglists.urls')), # leave in this order because...
        url(r'^resourcecenter/',    include('apps.resourcecenter.urls')), # ...resourcecenter has catch-all on subpages
    )

if 'apps.genfors' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^genfors/',           include('apps.genfors.urls')),
    )

# feedme  
if 'feedme' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', url(r'^feedme/', include('feedme.urls'))) 

# redwine
if 'redwine' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', url(r'^redwine/', include('redwine.urls')))

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
