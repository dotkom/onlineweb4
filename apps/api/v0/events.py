from copy import copy
from django.template.defaultfilters import slugify
from unidecode import unidecode
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization

from filebrowser.base import FileObject
from filebrowser.settings import VERSIONS

from apps.events.models import Event
from apps.events.models import Attendee
from apps.events.models import AttendanceEvent
from apps.events.models import CompanyEvent

from apps.companyprofile.models import Company

from apps.api.v0.authentication import UserResource


class AttendeeResource(ModelResource):
    user = fields.ToOneField(UserResource, 'user', full=True)

    class Meta(object):
        queryset = Attendee.objects.all()
        resource_name = 'attendees'


class CompanyResource(ModelResource):
    
    class Meta(object):
        queryset = Company.objects.all()
        resource_name = 'company'
        fields = ['old_image']


class CompanyEventResource(ModelResource):
    companies = fields.ToOneField(CompanyResource, 'company', full=True)

    class Meta(object):
        queryset = CompanyEvent.objects.all()
        resource_name = 'companies'


class AttendanceEventResource(ModelResource):
    users = fields.ToManyField(AttendeeResource, 'attendees', full=False)

    class Meta(object):
        queryset = AttendanceEvent.objects.all()
        resource_name = 'attendance_event'

        # XXX: Noop authorization is probably not safe for producion
        authorization = Authorization()


class EventResource(ModelResource):
    author = fields.ToOneField(UserResource, 'author', full=True)
    company_event = fields.ToManyField(CompanyEventResource, 'companies', full=True, null=True, blank=True)
    attendance_event = fields.ToOneField(AttendanceEventResource, 'attendance_event', full=True, null=True, blank=True)

    def alter_list_data_to_serialize(self, request, data):
        # Renames list data 'object' to 'events'.
        if isinstance(data, dict):
            data['events'] = copy(data['objects'])
            del(data['objects'])
        return data

    # Making multiple images for the events
    def dehydrate(self, bundle):
        
        # Setting slug-field
        bundle.data['slug'] = slugify(unidecode(bundle.data['title']))
        
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
        
        # Do the same thing for the company image
        if bundle.data['company_event']:
            for company in bundle.data['company_event']:
                temp_image = FileObject(company.data['companies'].data['old_image'])
                for ver in VERSIONS.keys():
                    if ver.startswith('companies_thumb'):
                        company.data['companies'].data['old_image_'+ver] = temp_image.version_generate(ver).url
                del(company.data['companies'].data['old_image'])

        # Returning washed object 
        return bundle
        
    def get_object_list(self, request):

        events = Event.objects.all()
        filtered_events = set()

        # Removes restricted events if the user does not belong to the right group
        for event in events:
            if event.can_display(request.user):
                filtered_events.add(event.pk)

        return Event.objects.filter(pk__in = filtered_events)

    class Meta(object):
        queryset = Event.objects.all()
        resource_name = 'events'
        # XXX: Noop authorization is probably not safe for producion
        authorization = Authorization()
        
        include_absolute_url = True
        ordering = ['event_start']
        filtering = {
            'event_end': ('gte',)
        }
