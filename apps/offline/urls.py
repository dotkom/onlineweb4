# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url

# API v1

from apps.api.utils import SharedAPIRootRouter
from apps.offline import views


urlpatterns = patterns(
    'apps.offline.views',
    url(r'^$', 'main', name='offline')
)


router = SharedAPIRootRouter()
router.register('offline', views.OfflineIssueViewSet)
