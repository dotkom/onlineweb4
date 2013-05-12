from django.conf.urls import patterns, include, url 

urlpatterns = patterns('apps.resourcecenter.views',
    url(r'^$', 'index', name='resourcecenter_index'),
)
