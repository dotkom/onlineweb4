from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView

from filebrowser.sites import site

# Tastypie 
from tastypie.api import Api
from apps.events.api import EventResource, UserResource
from apps.marks.api import MarkResource, MarkUserResource, GivenToResource, UserLookupResource

v0_api = Api(api_name='v0')
v0_api.register(EventResource())
v0_api.register(UserResource())
v0_api.register(MarkResource())
v0_api.register(MarkUserResource())
v0_api.register(GivenToResource())
v0_api.register(UserLookupResource())

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
    url(r'^$', TemplateView.as_view(template_name='base_site.html'), name='home'),
    url(r'^api/',      include(v0_api.urls)),
    url(r'^mail/',     include('apps.autoconfig.urls'))
)
