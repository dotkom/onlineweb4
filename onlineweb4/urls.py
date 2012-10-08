from django.conf.urls import patterns, include, url
from tastypie.api import Api
from apps.events.api import EventResource, UserResource

from django.contrib import admin
admin.autodiscover()

v0_api = Api(api_name='v0')
v0_api.register(EventResource())
v0_api.register(UserResource())

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(v0_api.urls)),
    url(r'^events/', include('apps.events.urls'))
)
