from django.conf.urls import patterns, include, url
from django.contrib import admin

from filebrowser.sites import site

# Tastypie 
from tastypie.api import Api
from apps.events.api import EventResource, UserResource

v0_api = Api(api_name='v0')
v0_api.register(EventResource())
v0_api.register(UserResource())

admin.autodiscover()

# URL config 
urlpatterns = patterns('',
    # Filebrowser must be above all admin-urls
    url(r'^admin/filebrowser/',     include(site.urls)),
    url(r'^grappelli/',             include('grappelli.urls')),

    # Admin urls
    url(r'^admin/',             include(admin.site.urls)),
    url(r'^admin/doc/',         include('django.contrib.admindocs.urls')),

    # Onlineweb app urls
    # url(r'^$', 'onlineweb4.views.home', name='home'),
    (r'^api/',      include(v0_api.urls)),
    (r'^mail/',     include('apps.autoconfig.urls'))
)
