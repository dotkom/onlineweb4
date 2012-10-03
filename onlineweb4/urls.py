from django.conf.urls import patterns, include, url
from tastypie.api import Api
from apps.events.api import EventResource, UserResource
from django.contrib import admin

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

# 
v0_api = Api(api_name='v0')
v0_api.register(EventResource())
v0_api.register(UserResource())

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
)
