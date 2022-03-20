from django.urls import re_path

from apps.hobbygroups.dashboard import views

urlpatterns = [re_path(r"^.*$", views.index, name="hobbies_dashboard_index")]
