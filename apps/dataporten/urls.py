from django.conf import settings
from django.urls import re_path

from apps.dataporten import views

app_name = "dataporten"

study_urls = [
    re_path(r"^study/$", views.study, name="study"),
    re_path(r"^study/callback/$", views.study_callback, name="study-callback"),
]

urlpatterns = []

if settings.DATAPORTEN.get("STUDY").get("ENABLED") or settings.DATAPORTEN.get(
    "STUDY"
).get("TESTING"):
    urlpatterns += study_urls
