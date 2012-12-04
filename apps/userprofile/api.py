# -*- coding: utf-8 -*-

from django.contrib.auth.models import User

from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization

from apps.userprofile.models import UserProfile

class UserProfileResource(ModelResource):
    class Meta:
        queryset = UserProfile.objects.all()
        resource_name = 'profile'
        include_resource_uri = False
        include_absolute_url = False

class UserResource(ModelResource):
    profile = fields.ToOneField(UserProfileResource, 'get_profile', full=True)

    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['username', 'first_name', 'last_name', 'last_login', 'email', ]
