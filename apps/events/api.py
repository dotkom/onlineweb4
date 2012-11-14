from copy import copy
from django.contrib.auth.models import User
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from apps.events.models import Event
from apps.events.models import Attendee
from apps.events.models import AttendanceEvent


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        # List of fields we do NOT want to make available
        excludes = ['password',
                    'email',
                    'date_joined'
                    'id',
                    'last_login']

class AttendeeResource(ModelResource):
    user = fields.ToOneField(UserResource, 'user', full=True)

    class Meta:
        queryset = Attendee.objects.all()
        resource_name = 'attendees'

class AttendanceEventResource(ModelResource):
    users = fields.ToManyField(AttendeeResource, 'attendees', full=False)

    class Meta:
        queryset = AttendanceEvent.objects.all()
        resource_name = 'attendance_event'

        # XXX: Noop authorization is probably not safe for producion
        authorization = Authorization()

class EventResource(ModelResource):
    author = fields.ToOneField(UserResource, 'author', full=True)
    attendance_event = fields.ToOneField(AttendanceEventResource, 'attendance_event', full=True, null=True, blank=True)

    def alter_list_data_to_serialize(self, request, data):
        # Renames list data 'object' to 'events'.
        if isinstance(data, dict):
            data['events'] = copy(data['objects'])
            del(data['objects'])
        return data

    class Meta:
        queryset = Event.objects.all()
        resource_name = 'events'
        # XXX: Noop authorization is probably not safe for producion
        authorization = Authorization()
