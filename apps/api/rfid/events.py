# -*- coding: utf-8 -*-

import logging
from copy import copy

from django.core.exceptions import PermissionDenied
from django.template.defaultfilters import slugify
from filebrowser.base import FileObject
from filebrowser.settings import VERSIONS
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.resources import ALL_WITH_RELATIONS, ModelResource
from unidecode import unidecode

from apps.api.rfid.auth import RfidAuthentication
from apps.api.rfid.user import UserResource
from apps.companyprofile.models import Company
from apps.events.models import AttendanceEvent, Attendee, CompanyEvent, Event


class AttendeeResource(ModelResource):
    user = fields.ToOneField(UserResource, 'user', full=True)

    class Meta(object):
        queryset = Attendee.objects.all()
        resource_name = 'attendees'
        allowed_methods = ['get']
        detail_allowed_methods = ['get', 'patch']
        allowed_update_fields = ['attended']
        authorization = Authorization()
        authentication = RfidAuthentication()
        filtering = {
            'user': ALL_WITH_RELATIONS,
        }

    def update_in_place(self, request, original_bundle, new_data):
        """
        Override to restrict modification of object fields to those set in allowed_update_fields
        """
        if set(new_data.keys()) - set(self._meta.allowed_update_fields):
            raise PermissionDenied(
                'Kun oppdatering av %s er tillatt.' % ', '.join(self._meta.allowed_update_fields)
            )

        logging.getLogger(__name__).debug('Attendee created: %s' % self.user)

        return super(AttendeeResource, self).update_in_place(request, original_bundle, new_data)


class CompanyResource(ModelResource):

    class Meta(object):
        queryset = Company.objects.all()
        resource_name = 'company'
        allowed_methods = ['get']
        fields = ['old_image']


class CompanyEventResource(ModelResource):
    companies = fields.ToOneField(CompanyResource, 'company', full=True)

    class Meta(object):
        queryset = CompanyEvent.objects.all()
        resource_name = 'companies'
        allowed_methods = ['get']


class AttendanceEventResource(ModelResource):
    users = fields.ToManyField(AttendeeResource, 'attendees', full=True)

    class Meta(object):
        queryset = AttendanceEvent.objects.all()
        resource_name = 'attendance_event'
        allowed_methods = ['get']
        filtering = {
            'users': ALL_WITH_RELATIONS,
        }


class EventResource(ModelResource):
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
        if 'image' in bundle.data and bundle.data['image']:
            # Parse to FileObject used by Filebrowser
            temp_image = FileObject(bundle.data['image'])

            # Itterate the different versions (by key)
            for ver in VERSIONS.keys():
                # Check if the key start with article_ (if it does, we want to crop to that size)
                if ver.startswith('events_'):
                    # Adding the new image to the object
                    bundle.data['image_' + ver] = temp_image.version_generate(ver).url

            # Unset the image-field
            del(bundle.data['image'])

        # Do the same thing for the company image
        if bundle.data['company_event']:
            for company in bundle.data['company_event']:
                temp_image = FileObject(company.data['companies'].data['old_image'])
                for ver in VERSIONS.keys():
                    if ver.startswith('companies_thumb'):
                        company.data['companies'].data['old_image_' + ver] = temp_image.version_generate(ver).url
                del(company.data['companies'].data['old_image'])

        # Returning washed object
        return bundle

    class Meta(object):
        queryset = Event.objects.all()
        resource_name = 'events'
        allowed_methods = ['get']
        authorization = Authorization()
        authentication = RfidAuthentication()

        ordering = ['event_start']
        filtering = {
            'event_end': ['gte'],
            'attendance_event': ALL_WITH_RELATIONS,
        }
