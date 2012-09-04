from django.conf.urls import patterns, url

urlpatterns = patterns('apps.events.views',
    url(r'^$', 'index'),

)
