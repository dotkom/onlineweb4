from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    url(r'^',       include('apps.api.v0.urls')),  
)
