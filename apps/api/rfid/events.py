from copy import copy
from django.template.defaultfilters import slugify
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from filebrowser.base import FileObject
from filebrowser.settings import VERSIONS
from apps.events.models import Event
from apps.events.models import Attendee
from apps.events.models import AttendanceEvent
from apps.events.models import CompanyEvent
from apps.companyprofile.models import Company
from apps.api.rfid.user import UserResource

class AttendeeResource(ModelResource):
    user = fields.ToOneField(UserResource, 'user', full=True)

    class Meta:
        queryset = Attendee.objects.all()
        resource_name = 'attendees'

class CompanyResource(ModelResource):
    
    class Meta:
        queryset = Company.objects.all()
        resource_name = 'company'
        fields = ['image']
class CompanyEventResource(ModelResource):
    companies = fields.ToOneField(CompanyResource, 'company', full=True)
    class Meta:
        queryset = CompanyEvent.objects.all()
        resource_name ='companies'

class AttendanceEventResource(ModelResource):
    users = fields.ToManyField(AttendeeResource, 'attendees', full=False)

    class Meta:
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
        
        # Setting sluyg-field
        bundle.data['slug'] = slugify(bundle.data['title'])
        
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
                temp_image = FileObject(company.data['companies'].data['image'])
                for ver in VERSIONS.keys():
                    if ver.startswith('companies_thumb'):
                        company.data['companies'].data['image_'+ver] = temp_image.version_generate(ver).url
                del(company.data['companies'].data['image'])

        # Returning washed object 
        return bundle
        

    class Meta:
        queryset = Event.objects.all()
        resource_name = 'events'
        # XXX: Noop authorization is probably not safe for producion
        authorization = Authorization()
        
        ordering = ['event_start']
        filtering = {
            'event_end' : ('gte',)
        }
