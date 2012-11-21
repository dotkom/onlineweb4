# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('apps.feedback.views',
    url(r'^$', 'index', name='feedback_index'),
)
