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
from wiki.decorators import get_article
from wiki.views.mixins import ArticleMixin


def server_error(request):
    log = logging.getLogger(__name__)

    if request.method == "POST":
        message = request.POST.get("reason")
        if not message:
            return redirect("home")
        try:
            log.error(
                "%s triggered a 500 server error and provided the following description: %s"
                % (request.user, message)
            )
            send_mail(
                "500error user-report",
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.EMAIL_DOTKOM],
            )
            log.debug("Finished sending error email to %s" % settings.EMAIL_DOTKOM)
            messages.success(
                request, "Feilmeldingen din ble sendt til %s" % settings.EMAIL_DOTKOM
            )
            return redirect("home")
        except SMTPException:
            messages.error(
                request, "Det oppstod en uventet feil under sending av feilmeldingen"
            )
            return redirect("home")
    return render(request, "500.html", {"error_form": ErrorForm})


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
