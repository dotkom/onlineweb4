# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.feedback import views

feedback = r'^(?P<applabel>\w+)/(?P<appmodel>\w+)/(?P<object_id>\d+)/(?P<feedback_id>\d+)/$'
results = r'^(?P<applabel>\w+)/(?P<appmodel>\w+)/(?P<object_id>\d+)/(?P<feedback_id>\d+)/results/$'
chart_data = r'^(?P<applabel>\w+)/(?P<appmodel>\w+)/(?P<object_id>\d+)/(?P<feedback_id>\d+)/results/chartdata/$'
results_token = r'^(?P<applabel>\w+)/(?P<appmodel>\w+)/(?P<object_id>\d+)/(?P<feedback_id>\d+)/results/(?P<token>\w+)/$'
chart_data_token = r'^(?P<applabel>\w+)/(?P<appmodel>\w+)/(?P<object_id>\d+)/(?P<feedback_id>\d+)/results/(?P<token>\w+)/chartdata/$'

urlpatterns = [
    url(r'^$', views.index, name='feedback_index'),
    url(feedback, views.feedback, name="feedback"),
    url(results, views.result, name="result"),
    url(chart_data, views.chart_data, name="chart_data"),
    url(results_token, views.results_token, name="results_token"),
    url(chart_data_token, views.chart_data_token, name="chart_data_token"),
    url(r'^deleteanswer/$', views.delete_answer, name="delete_anwer"),
]
