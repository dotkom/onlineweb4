# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url
from apps.offline.views import main

urlpatterns = patterns('apps.offline.views',
    url(r'^$', 'main', name='offline')
)

# API v1

from apps.api.utils import SharedAPIRootRouter
from apps.offline import views
router = SharedAPIRootRouter()
router.register('offline', views.OfflineIssueViewSet)
