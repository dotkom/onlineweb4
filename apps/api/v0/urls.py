# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url, include

from tastypie.api import Api

from apps.api.v0.article import ArticleResource, ArticleLatestResource
from apps.api.v0.authentication import UserResource
from apps.api.v0.events import EventResource, AttendanceEventResource, AttendeeResource, CompanyResource, CompanyEventResource
from apps.api.v0.marks import MarkResource, EntryResource, MyMarksResource, MyActiveMarksResource
from apps.api.v0.offline import IssueResource

v0_api = Api(api_name='v0')

# users
v0_api.register(UserResource())

# event
v0_api.register(EventResource())
v0_api.register(AttendanceEventResource())
v0_api.register(CompanyResource())
v0_api.register(CompanyEventResource())

# article
v0_api.register(ArticleResource())
v0_api.register(ArticleLatestResource())

# marks
#v0_api.register(MarkResource())
#v0_api.register(EntryResource())
#v0_api.register(MyMarksResource())
#v0_api.register(MyActiveMarksResource())

# offline
v0_api.register(IssueResource())

# Set the urls to be included.
urlpatterns = patterns('',
    url(r'^',       include(v0_api.urls)),
)
