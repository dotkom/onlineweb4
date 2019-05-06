# -*- encoding: utf-8 -*-

from django.shortcuts import render
# API v1
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny

from apps.offline.models import Issue
from apps.offline.serializers import OfflineIssueSerializer


def main(request):
    issues = Issue.objects.all()
    years = set()
    for issue in issues:
        years.add(issue.release_date.year)

    years = list(reversed(sorted(years)))

    ctx = {
        "issues": issues,
        "years": years,

    }
    return render(request, "offline/offline.html", ctx)


class OfflineIssueViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = Issue.objects.all()
    serializer_class = OfflineIssueSerializer
    permission_classes = (AllowAny,)
    filterset_fields = ('id', 'release_date', 'title')
