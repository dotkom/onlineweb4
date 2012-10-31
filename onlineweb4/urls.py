from django.conf.urls import patterns, include, url
from tastypie.api import Api
from django.contrib import admin

from apps.events.api import EventResource, UserResource, AttendanceEventResource
from apps.events import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

v0_api = Api(api_name='v0')
v0_api.register(EventResource())
v0_api.register(UserResource())
v0_api.register(AttendanceEventResource())

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'onlineweb4.views.home', name='home'),
    # url(r'^onlineweb4/', include('onlineweb4.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    (r'^admin/', admin.site.urls),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^api/', include(v0_api.urls)),
    (r'^events/(?P<event_id>\d+)', views.details),
    (r'^events/', views.index),
)
