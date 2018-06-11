from django.conf.urls import url

from apps.dataporten import views

urlpatterns = [
    url(r'^study/$', views.study, name='study'),
    url(r'^study/callback/$', views.study_callback, name='study-callback'),
]
