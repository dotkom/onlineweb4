from django.conf.urls import url

from apps.splash import views

urlpatterns = [
    url(r'^events.ics$', views.calendar_export, name='splash_calendar'),
]
