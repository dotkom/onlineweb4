from apps.events.api import EventResource, UserResource
from django.conf.urls import patterns, include, url
from django.contrib import admin
from filebrowser.sites import site
from tastypie.api import Api
from apps.events.api import EventResource, UserResource

admin.autodiscover()

urlpatterns = patterns('',
    # Filebrowser must be above all admin-urls
    url(r'^admin/filebrowser/', include(site.urls)),
)

# 
v0_api = Api(api_name='v0')
v0_api.register(EventResource())
v0_api.register(UserResource())

urlpatterns += patterns('',

    # Admin urls
    url(r'^admin/', include(admin.site.urls)),
    
    # Onlineweb app urls
    # Index
    # url(r'^$', 'onlineweb4.views.home', name='home'),
    # Other


    (r'^api/', include(v0_api.urls)),
    (r'^mail/', include('apps.autoconfig.urls'))
)
