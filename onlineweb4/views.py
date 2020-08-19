# -*- coding: utf-8 -*-
import logging
from smtplib import SMTPException

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from onlineweb4.forms import ErrorForm
from onlineweb4.settings.sentry import OW4_SENTRY_DSN
from sentry_sdk import last_event_id
from wiki.decorators import get_article
from wiki.views.mixins import ArticleMixin


def handler500(request, *args, **argv):
    return render(
        request,
        "500.html",
        {"sentry_event_id": last_event_id(), "sentry_dsn": OW4_SENTRY_DSN},
        status=500,
    )


class WikiTreeView(ArticleMixin, TemplateView):
    template_name = "wiki/tree.html"

    @method_decorator(get_article(can_read=True))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_tab"] = "view"
        article_context = ArticleMixin.get_context_data(self, **kwargs)
        descendants = article_context["urlpath"].root().get_descendants()
        descendants = [
            descendant
            for descendant in descendants
            if descendant.article.can_read(self.request.user)
        ]
        article_context["descendants"] = descendants
        return article_context
