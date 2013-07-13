from django.conf.urls import patterns, include, url 

urlpatterns = patterns('apps.resourcecenter.views',
	# Index page
    url(r'^$', 'index', name='resourcecenter_index'),
    # Subpages
    url(r'^mailinglists/$', 'mailinglists', name='resourcecenter_mailinglists'),
    url(r'^gameservers/$', 'gameservers', name='resourcecenter_gameservers'),
)
