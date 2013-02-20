#-*- coding: utf-8 -*-
from django.contrib.auth.models import User

from tastypie import fields
from tastypie.resources import ModelResource

from apps.offline.models import Issue
from apps.api.v0.userprofile import UserResource


class IssueResource(ModelResource):

    class Meta:
        queryset = Issue.objects.all()
        resource_name = 'offline/issues'
