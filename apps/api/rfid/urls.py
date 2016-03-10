# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from tastypie.api import Api

from apps.api.rfid.events import AttendanceEventResource, AttendeeResource, EventResource
from apps.api.rfid.user import UserResource

rfid_api = Api(api_name='rfid')

rfid_api.register(UserResource())
rfid_api.register(AttendeeResource())
rfid_api.register(AttendanceEventResource())
rfid_api.register(EventResource())

urlpatterns = [
    url(r'^', include(rfid_api.urls)),
]
