# -*- coding: utf-8 -*-
from smtplib import SMTPException

from onlineweb4.forms import ErrorForm
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.conf import settings



def server_error(request):
    if request.method == 'POST':
        form = ErrorForm(request.POST)
        message = request.POST.get('reason')
        try: 
            send_mail('500error user-report', message,
                settings.DEFAULT_FROM_EMAIL, [settings.EMAIL_DOTKOM])
            return redirect('home')
        except SMTPException:
            return redirect('home')

    return render(request, '500.html', {'error_form': ErrorForm})


