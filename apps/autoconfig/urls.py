from django.conf.urls.defaults import patterns, url
from apps.autoconfig.views import autoconfig

urlpatterns = patterns('apps.autoconfig.views',
    (r'^config-v1.1.xml$', autoconfig),
)
