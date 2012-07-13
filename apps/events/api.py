from copy import copy
from django.contrib.auth.models import User
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from models import Event

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'author'

class EventResource(ModelResource):
    author = fields.ToOneField(UserResource, 'author', full=True)

    def alter_list_data_to_serialize(self, request, data):
        # Rename list data object to 'events'.
        if isinstance(data, dict):
            data['events'] = copy(data['objects'])
            del(data['objects'])
        return data

    class Meta:
        queryset = Event.objects.all()
        resource_name = 'events'
        # XXX: Noop authorization is not producion safe
        authorization = Authorization()
