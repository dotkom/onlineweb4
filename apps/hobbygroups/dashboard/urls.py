from django.urls import re_path

from apps.hobbygroups.dashboard import views

urlpatterns = [re_path("^.*$", views.index, name="hobbies_dashboard_index")]
