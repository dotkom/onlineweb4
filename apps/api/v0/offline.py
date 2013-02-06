#-*- coding: utf-8 -*-
from django.contrib.auth.models import User

from tastypie import fields
from tastypie.resources import ModelResource

from apps.offline.models import Offline, Issue
from apps.api.v0.userprofile import UserResource

class OfflineResource(ModelResource):

    class Meta:
        queryset = Offline.objects.all()
        resource_name = 'offline/meta'


class IssueResource(ModelResource):

    class Meta:
        queryset = Issue.objects.all()
        resource_name = 'offline/issues'
