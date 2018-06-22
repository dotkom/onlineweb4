from django.conf import settings
from django.conf.urls import url

from apps.dataporten import views

study_urls = [
    url(r'^study/$', views.study, name='study'),
    url(r'^study/callback/$', views.study_callback, name='study-callback'),
]

urlpatterns = []

if settings.DATAPORTEN.get('STUDY').get('ENABLED') or settings.DATAPORTEN.get('STUDY').get('TESTING'):
    urlpatterns += study_urls
