from django.urls import re_path

from apps.splash import views

urlpatterns = [re_path("^events.ics$", views.calendar_export, name="splash_calendar")]
