from django.shortcuts import render
from django.http import HttpResponseBadRequest

def autoconfig(request):
  if 'emailaddress' in request.GET:
    email = request.GET['emailaddress']
    if '@online.ntnu.no' in email:
      response = render(request, 'autoconfig/client_config.xml')
      response['Content-Type'] = 'application/xml; charset=utf-8'
      return response
  return HttpResponseBadRequest()
