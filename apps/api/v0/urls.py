# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from tastypie.api import Api

from apps.api.v0.article import ArticleLatestResource, ArticleResource
from apps.api.v0.events import (AttendanceEventResource, CompanyEventResource, CompanyResource,
                                EventResource)
from apps.api.v0.offline import IssueResource

v0_api = Api(api_name='v0')

# users
# User endpoint not registered at the moment. Maybe in the future with some restrictions / auth

# event
v0_api.register(EventResource())
v0_api.register(AttendanceEventResource())
v0_api.register(CompanyResource())
v0_api.register(CompanyEventResource())

# article
v0_api.register(ArticleResource())
v0_api.register(ArticleLatestResource())

# offline
v0_api.register(IssueResource())

# Set the urls to be included.
urlpatterns = [
    url(r'^', include(v0_api.urls)),
]
