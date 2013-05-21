from django.conf.urls import patterns, include, url 

urlpatterns = patterns('apps.resourcecenter.views',
	# Index page
    url(r'^$', 'index', name='resourcecenter_index'),
    # Subpages
    url(r'^notifier/$', 'notifier', name='resourcecenter_notifier'),
    url(r'^mailinglists/$', 'mailinglists', name='resourcecenter_mailinglists'),
    url(r'^infopages/$', 'infopages', name='resourcecenter_infopages'),
    url(r'^gameservers/$', 'gameservers', name='resourcecenter_gameservers'),
    url(r'^githubrepos/$', 'githubrepos', name='resourcecenter_githubrepos'),
    url(r'^irc/$', 'irc', name='resourcecenter_irc'),
)
