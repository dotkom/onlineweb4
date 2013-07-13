# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('apps.mailinglists.views',
	# Index page
    url(r'^$', 'index', name='mailinglists_index')
)
