from django.shortcuts import render_to_response
from django.http import HttpResponseBadRequest
from django.template import RequestContext

def autoconfig(request):
  if 'emailaddress' in request.GET:
    email = request.GET['emailaddress']
    if '@online.ntnu.no' in email:
      response = render_to_response('autoconfig/client_config.xml', {}, RequestContext(request))
      response['Content-Type'] = 'application/xml; charset=utf-8'
      return response
  return HttpResponseBadRequest()
