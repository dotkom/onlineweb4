#-*- coding: utf-8 -*-

from django.contrib.auth.models import User

from tastypie import fields
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS

from apps.marks.models import Mark, UserEntry

class MarkUserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'auth/user'
        fields = ['username', 'first_name', 'last_name', 'last_login', ]
        allowed_methods = ['get', ]

class GivenToResource(ModelResource):
    user = fields.ToOneField(MarkUserResource, 'user', full=True)

    class Meta:
        queryset = UserEntry.objects.all() 
        resource_name = 'marks/entry'

class MarkResource(ModelResource):
    given_by = fields.ForeignKey(MarkUserResource, 'given_by', full=True) 
    last_changed_by = fields.ForeignKey(MarkUserResource, 'last_changed_by', full=True)
    given_to = fields.ToManyField(GivenToResource, 'given_to', full=False)

    class Meta:
        queryset = Mark.objects.all()
        resource_name = 'marks/marks'
        filtering = {
            'user': ALL_WITH_RELATIONS
            }

class UserLookupResource(ModelResource):
     
    class Meta:
        queryset = UserEntry.objects.all()
        resource_name = 'marks/user'
