from django.conf import settings
from apps.events.api import EventResource, UserResource
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from filebrowser.sites import site
from tastypie.api import Api

admin.autodiscover()

# 
v0_api = Api(api_name='v0')
v0_api.register(EventResource())
v0_api.register(UserResource())

urlpatterns = patterns('',
    # Filebrowser must be above all admin-urls
    url(r'^admin/filebrowser/', include(site.urls)),
    url(r'^grappelli/', include('grappelli.urls')),

    # Admin urls
    url(r'^admin/', include(admin.site.urls)),
    url(r'^article/',include('apps.article.urls')),
    # Onlineweb app urls
    # Index
    # url(r'^$', 'onlineweb4.views.home', name='home'),
    # Other


    (r'^api/', include(v0_api.urls)),
    (r'^mail/', include('apps.autoconfig.urls'))
)


# http://docs.djangoproject.com/en/1.3/howto/static-files/#staticfiles-development
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

    urlpatterns += patterns('',
        url(r'^uploaded_media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
            'show_indexes': True
        }),
        (r'^500/$', 'django.views.defaults.server_error'),
    )
