from django.conf.urls import patterns, include, url 

urlpatterns = patterns('apps.events.views',
    url(r'^$', 'index', name='events_index'),
    url(r'^(?P<event_id>\d+)/$', 'details', name='events_details'),
)
