# -*- encoding: utf-8 -*-

from apps.offline.models import Issue
from django.shortcuts import render

def main(request):
    issues = Issue.objects.all()
    return render(request, "offline/offline.html", {"issues": issues})

