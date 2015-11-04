# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url, include
from tastypie.api import Api
from apps.api.rfid.user import UserResource
from apps.api.rfid.events import AttendeeResource, EventResource, AttendanceEventResource

rfid_api = Api(api_name='rfid')

rfid_api.register(UserResource())
rfid_api.register(AttendeeResource())
rfid_api.register(AttendanceEventResource())
rfid_api.register(EventResource())

urlpatterns = patterns(
    '',
    url(r'^', include(rfid_api.urls)),
)
