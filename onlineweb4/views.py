# -*- coding: utf-8 -*-
from django.shortcuts import render
from sentry_sdk import capture_message
from onlineweb4.settings.sentry import OW4_SENTRY_DSN


def handler500(request, *args, **kwargs):
    event_id = capture_message("500", level="error")
    return render(
        request,
        "500.html",
        {"sentry_event_id": event_id, "sentry_dsn": OW4_SENTRY_DSN},
        status=500,
    )
