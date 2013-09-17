# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url 

urlpatterns = patterns('apps.resourcecenter.views',
	# Index page
    url(r'^$', 'index', name='resourcecenter_index'),
    # Subpages
    url(r'^gameservers/$', 'gameservers', name='resourcecenter_gameservers'),
    # Catch-all
    url(r'^.*/$', 'index', name='resourcecenter_index'),
)
