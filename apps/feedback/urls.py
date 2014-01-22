# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('apps.feedback.views',
    url(r'^$', 'index', name='feedback_index'),
    url(r'^(?P<applabel>\w+)/(?P<appmodel>\w+)/(?P<object_id>\d+)/(?P<feedback_id>\d+)/$', "feedback", name="feedback"),
    url(r'^(?P<applabel>\w+)/(?P<appmodel>\w+)/(?P<object_id>\d+)/(?P<feedback_id>\d+)/results/$', "result", name="result"),
    url(r'^(?P<applabel>\w+)/(?P<appmodel>\w+)/(?P<object_id>\d+)/(?P<feedback_id>\d+)/results/chartdata/$', "chart_data", name="chart_data"),
    url(r'^(?P<applabel>\w+)/(?P<appmodel>\w+)/(?P<object_id>\d+)/(?P<feedback_id>\d+)/results/(?P<token>\w+)/$', "results_token", name="results_token"),
    url(r'^(?P<applabel>\w+)/(?P<appmodel>\w+)/(?P<object_id>\d+)/(?P<feedback_id>\d+)/results/(?P<token>\w+)/chartdata/$', "chart_data_token", name="chart_data_token"),
    url(r'^deleteanswer/$', "delete_answer", name="delete_anwer"),
)
