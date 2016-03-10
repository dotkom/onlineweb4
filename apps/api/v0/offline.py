# -*- coding: utf-8 -*-

from tastypie.resources import ModelResource

from apps.offline.models import Issue


class IssueResource(ModelResource):

    class Meta:
        queryset = Issue.objects.all()
        resource_name = 'offline/issues'
