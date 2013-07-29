from django.conf.urls import patterns, include, url 

urlpatterns = patterns('apps.companyprofile.views',
    # url(r'^$', 'index', name='events_index'),
    url(r'^(?P<company_id>\d+)/$', 'details', name='company_details'),
    # url(r'^(?P<event_id>\d+)/attend/$', 'attendEvent', name='attend_event'),
    # url(r'^(?P<event_id>\d+)/unattend/$', 'unattendEvent', name='unattend_event'),
)