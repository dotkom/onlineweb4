# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

fb = r'^(?P<applabel>\w+)/(?P<appmodel>\w+)/(?P<object_id>\d+)/(?P<feedback_id>\d+)/$'
r = r'^(?P<applabel>\w+)/(?P<appmodel>\w+)/(?P<object_id>\d+)/(?P<feedback_id>\d+)/results/$'
cd = r'^(?P<applabel>\w+)/(?P<appmodel>\w+)/(?P<object_id>\d+)/(?P<feedback_id>\d+)/results/chartdata/$'
rt = r'^(?P<applabel>\w+)/(?P<appmodel>\w+)/(?P<object_id>\d+)/(?P<feedback_id>\d+)/results/(?P<token>\w+)/$'
cdt = r'^(?P<applabel>\w+)/(?P<appmodel>\w+)/(?P<object_id>\d+)/(?P<feedback_id>\d+)/results/(?P<token>\w+)/chartdata/$'

urlpatterns = patterns(
    'apps.feedback.views',
    url(r'^$', 'index', name='feedback_index'),
    url(fb, "feedback", name="feedback"),
    url(r, "result", name="result"),
    url(cd, "chart_data", name="chart_data"),
    url(rt, "results_token", name="results_token"),
    url(cdt, "chart_data_token", name="chart_data_token"),
    url(r'^deleteanswer/$', "delete_answer", name="delete_anwer"),
)
