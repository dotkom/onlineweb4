# -*- coding: utf-8 -*-
from django.shortcuts import render
from sentry_sdk import last_event_id

from onlineweb4.settings.sentry import OW4_SENTRY_DSN


def handler500(request, *args, **kwargs):
    return render(
        request,
        "500.html",
        {"sentry_event_id": last_event_id(), "sentry_dsn": OW4_SENTRY_DSN},
        status=500,
    )
