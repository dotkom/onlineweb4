# -*- encoding: utf-8 -*-

from apps.offline.models import Issue
from django.shortcuts import render

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
