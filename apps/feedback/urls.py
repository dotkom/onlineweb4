# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('apps.feedback.views',
    url(r'^(?P<applabel>\w+)/(?P<appmodel>\w+)/(?P<object_id>\d+)/(?P<feedback_id>\d+)/$',
        "feedback"),
    url(r'^$', 'index', name='feedback_index'),
)
