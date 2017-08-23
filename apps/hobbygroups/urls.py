from django.conf.urls import url

from apps.hobbygroups import views

urlpatterns = [
    url(r'^$', views.index, name='hobbygroups_index'),
]
