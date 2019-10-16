from django.conf.urls import url

from apps.hobbygroups.dashboard import views

urlpatterns = [
    url(r'^.*$', views.index, name='hobbies_dashboard_index')
]
