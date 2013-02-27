from django.conf.urls import patterns, include, url 

urlpatterns = patterns('apps.careeropportunity.views',
    url(r'^$', 'index', name='careeropportunity_index'),
    url(r'^(?P<opportunity_id>\d+)/$', 'details', name='careeropportunity_details'),
)
