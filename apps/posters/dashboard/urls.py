# -*- encoding: utf-8 -*-

from apps.posters.dashboard import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.index, name='posters'),
    url(r'^add/(?P<order_type>\d+)$', views.add, name='posters_add'),
    url(r'^detail/(?P<order_id>\d+)$', views.detail, name='posters_detail'),
    url(r'^edit/(?P<order_id>\d+)$', views.edit, name='posters_edit'),
    # Ajax
    url(r'^assign_person/$', views.assign_person, name='assign_person'),
]
