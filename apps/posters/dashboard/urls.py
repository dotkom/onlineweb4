# -*- encoding: utf-8 -*-

from django.urls import re_path

from apps.posters.dashboard import views

urlpatterns = [
    re_path(r"^$", views.index, name="posters"),
    re_path(r"^add/(?P<order_type>\d+)$", views.add, name="posters_add"),
    re_path(r"^detail/(?P<order_id>\d+)$", views.detail, name="posters_detail"),
    re_path(r"^edit/(?P<order_id>\d+)$", views.edit, name="posters_edit"),
    # Ajax
    re_path(r"^assign_person/$", views.assign_person, name="assign_person"),
]
