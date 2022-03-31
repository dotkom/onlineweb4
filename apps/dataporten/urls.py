from django.urls import re_path

from apps.dataporten import views

app_name = "dataporten"

urlpatterns = [
    re_path(r"^study/$", views.study, name="study"),
    re_path(r"^study/callback/$", views.study_callback, name="study-callback"),
]
