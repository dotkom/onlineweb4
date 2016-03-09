# -*- coding: utf-8 -*-

from apps.offline.models import Issue
from tastypie.resources import ModelResource


class IssueResource(ModelResource):

    class Meta:
        queryset = Issue.objects.all()
        resource_name = 'offline/issues'
