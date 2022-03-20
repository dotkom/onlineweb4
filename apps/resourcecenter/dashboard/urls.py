from django.urls import re_path

from apps.resourcecenter.dashboard import views

urlpatterns = [re_path(r"^.*$", views.index, name="resources_dashboard_index")]
