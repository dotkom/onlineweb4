# -*- coding: utf-8 -*-

from tastypie import fields
from tastypie.resources import ModelResource, ALL
from apps.authentication.models import OnlineUser as User
from apps.authentication.models import RfidAuthentication
from tastypie.authorization import Authorization

class UserResource(ModelResource):

    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['username', 'first_name', 'last_name', 'rfid', ]
	allowed_methods = ['get', 'patch']
        authorization = Authorization()
        authentication = RfidAuthentication()
        filtering = {
            "username": ALL,
            "rfid": ALL,
        }

