# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.feedback import views

base_url = r'^(?P<applabel>\w+)/(?P<appmodel>\w+)/(?P<object_id>\d+)/(?P<feedback_id>\d+)/'

urlpatterns = [
    url(r'^$', views.index, name='feedback_index'),
    url(base_url + r'$', views.feedback, name="feedback"),
    url(base_url + r'results/$', views.result, name="result"),
    url(base_url + r'results/chartdata/$', views.chart_data, name="chart_data"),
    url(base_url + r'results/(?P<token>\w+)/$', views.results_token, name="results_token"),
    url(base_url + r'results/(?P<token>\w+)/chartdata/$', views.chart_data_token, name="chart_data_token"),
    url(r'^deleteanswer/$', views.delete_answer, name="delete_anwer"),
]
