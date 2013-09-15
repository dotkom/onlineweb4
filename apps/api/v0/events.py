from copy import copy
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization

from filebrowser.base import FileObject
from filebrowser.settings import VERSIONS

from apps.events.models import Event
from apps.events.models import Attendee
from apps.events.models import AttendanceEvent

from apps.api.v0.authentication import UserResource

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

    # Making multiple images for the events
    def dehydrate(self, bundle):
        
        # If image is set
        if bundle.data['image']:
            # Parse to FileObject used by Filebrowser
            temp_image = FileObject(bundle.data['image'])
            
            # Itterate the different versions (by key)
            for ver in VERSIONS.keys():
                # Check if the key start with article_ (if it does, we want to crop to that size)
                if ver.startswith('events_'):
                    # Adding the new image to the object
                    bundle.data['image_'+ver] = temp_image.version_generate(ver).url
            
            # Unset the image-field
            del(bundle.data['image'])
            
            # Returning washed object
        return bundle

    class Meta:
        queryset = Event.objects.all()
        resource_name = 'events'
        # XXX: Noop authorization is probably not safe for producion
        authorization = Authorization()
        
        ordering = ['event_start']
        filtering = {
            'event_end' : ('gte',),
            'event_type': ('exact',)
        }
