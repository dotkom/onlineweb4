# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

from apps.feedback.models import Feedback

urlpatterns = patterns('apps.feedback.views',
    url(r'^$', 'index', name='feedback_index'),
)
