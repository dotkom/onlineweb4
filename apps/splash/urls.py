from django.urls import re_path

from apps.splash import views

urlpatterns = [re_path(r"^events.ics$", views.calendar_export, name="splash_calendar")]
