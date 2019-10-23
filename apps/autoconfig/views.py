# -*- encoding: utf-8 -*-

from django.http import HttpResponseBadRequest
from django.shortcuts import render


def autoconfig(request):
    if 'emailaddress' in request.GET:
        email = request.GET['emailaddress']
        if '@online.ntnu.no' in email:
            return render(request, 'autoconfig/client_config.xml', content_type='application/xml; charset=utf-8')
    return HttpResponseBadRequest()
