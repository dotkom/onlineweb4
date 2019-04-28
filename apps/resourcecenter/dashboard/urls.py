from django.conf.urls import url

from apps.resourcecenter.dashboard import views

urlpatterns = [
    url(r'^$', views.index, name='resources_dashboard_index')
]
