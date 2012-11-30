
from copy import copy
from django.contrib.auth.models import User
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization


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
