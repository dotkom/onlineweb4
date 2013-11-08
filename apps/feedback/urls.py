# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('apps.feedback.views',
    url(r'^(?P<applabel>\w+)/(?P<appmodel>\w+)/(?P<object_id>\d+)/(?P<feedback_id>\d+)/$', "feedback", name="feedback"),
    url(r'^(?P<applabel>\w+)/(?P<appmodel>\w+)/(?P<object_id>\d+)/(?P<feedback_id>\d+)/results/$', "result", name="result"),
    url(r'^(?P<applabel>\w+)/(?P<appmodel>\w+)/(?P<object_id>\d+)/(?P<feedback_id>\d+)/results/chartdata/$', "get_chart_data", name="get_chart_data"),
    url(r'^deleteanswer/$', "delete_answer", name="delete_anwer"),
    url(r'^$', 'index', name='feedback_index'),
)
