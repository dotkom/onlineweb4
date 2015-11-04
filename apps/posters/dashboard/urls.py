# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.posters.dashboard.views',
    url(r'^$', 'index', name='posters'),
    url(r'^add/(?P<order_type>\d+)$', 'add', name='posters_add'),
    url(r'^detail/(?P<order_id>\d+)$', 'detail', name='posters_detail'),
    url(r'^edit/(?P<order_id>\d+)$', 'edit', name='posters_edit'),
    # Ajax
    url(r'^assign_person/$', 'assign_person', name='assign_person'),
)
