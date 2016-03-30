# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.authentication.dashboard import views

urlpatterns = [
    url(r'^$', views.index, name='auth_index'),
    url(r'^groups/$', views.groups_index, name='groups_index'),
    url(r'^groups/(?P<pk>\d+)/$', views.groups_detail, name='groups_detail'),
    url(r'^user/$', views.UserSearchView.as_view(), name='user_search'),
    url(r'^user/list/$', views.UserListView.as_view(), name='user_list'),
    url(r'^user/(?P<user_id>\d+)/$', views.UserDetailView.as_view(), name='dashboard_user_detail'),
    url(r'^user/(?P<user_id>\d+)/edit$', views.UserUpdateView.as_view(), name='dashboard_user_edit'),
    url(r'^user/(?P<user_id>\d+)/delete', views.UserDeleteView.as_view(), name='dashboard_user_delete'),
]
