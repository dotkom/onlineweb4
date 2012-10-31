from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.views.generic import TemplateView

from filebrowser.sites import site

# Tastypie 
from tastypie.api import Api
from apps.events.api import EventResource, UserResource, AttendanceEventResource
from apps.events import views
from apps.article.api import ArticleResource, UserResource
from apps.marks.api import MarkResource, MarkUserResource, EntryResource, MyMarksResource, MyActiveMarksResource
from apps.userprofile.api import UserResource, UserProfileResource

v0_api = Api(api_name='v0')
v0_api.register(EventResource())
v0_api.register(UserResource())
v0_api.register(ArticleResource())
v0_api.register(AttendanceEventResource())
v0_api.register(MarkResource())
v0_api.register(MarkUserResource())
v0_api.register(EntryResource())
v0_api.register(MyMarksResource())
v0_api.register(MyActiveMarksResource())


# URL config 
admin.autodiscover()

urlpatterns = patterns('',
    # Filebrowser must be above all admin-urls
    url(r'^admin/filebrowser/',     include(site.urls)),
    url(r'^grappelli/',             include('grappelli.urls')),

    # Admin urls
    url(r'^admin/',             include(admin.site.urls)),
    url(r'^admin/doc/',         include('django.contrib.admindocs.urls')),

    # Onlineweb app urls
    url(r'^$', TemplateView.as_view(template_name='base_site.html'), name='home'),
    url(r'^api/',       include(v0_api.urls)),
    url(r'^article/',   include('apps.article.urls')),
    url(r'^mail/',      include('apps.autoconfig.urls')),
    url(r'^auth/',      include('apps.authentication.urls')), 

    # TODO move these urls to events/urls.py
    (r'^events/(?P<event_id>\d+)/?', views.details),
    (r'^events/', views.index),
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
