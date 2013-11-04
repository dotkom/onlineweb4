# -*- coding: utf-8 -*-

from tastypie import fields
from tastypie.resources import ModelResource, ALL
from apps.authentication.models import OnlineUser as User
from apps.api.rfid.auth import RfidAuthentication
from tastypie.authorization import Authorization

class UserResource(ModelResource):

    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['username', 'first_name', 'last_name', 'rfid', ]
        allowed_update_fields = ['rfid']
        allowed_methods = ['get']
        detail_allowed_methods = ['get', 'patch']
        authorization = Authorization()
        authentication = RfidAuthentication()
        filtering = {
            "username": ALL,
            "rfid": ALL,
        }

    def update_in_place(self, request, original_bundle, new_data):
        """
        Override to restrict patching of user fields to those specified in allowed_update_fields
        """
        if set(new_data.keys()) - set(self._meta.allowed_update_fields):
            raise BadRequest(
                'Kun oppdatering av %s er tillatt.' % ', '.join(self._meta.allowed_update_fields)
            )

        return super(UserResource, self).update_in_place(request, original_bundle, new_data)
