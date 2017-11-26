# -*- coding: utf-8 -*-
import logging
from smtplib import SMTPException

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from onlineweb4.forms import ErrorForm


def server_error(request):
    log = logging.getLogger(__name__)

    if request.method == 'POST':
        message = request.POST.get('reason')
        if not message:
            return redirect('home')
        try:
            log.error('%s triggered a 500 server error and provided the following description: %s' % (
                request.user,
                message
            ))
            send_mail('500error user-report', message,
                settings.DEFAULT_FROM_EMAIL, [settings.EMAIL_DOTKOM])
            log.debug('Finished sending error email to %s' % settings.EMAIL_DOTKOM)
            messages.success(request, 'Feilmeldingen din ble sendt til %s' % settings.EMAIL_DOTKOM)
            return redirect('home')
        except SMTPException:
            messages.error(request, 'Det oppstod en uventet feil under sending av feilmeldingen')
            return redirect('home')
    return render(request, '500.html', {'error_form': ErrorForm})
