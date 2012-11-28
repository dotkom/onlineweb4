#-*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib.auth.models import User

from tastypie import fields
from tastypie.authentication import Authentication, BasicAuthentication#, SessionAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS

from apps.marks.models import Mark, UserEntry

# Temporary resource for fetching users. This should be replaced by a global UserResource.
# TODO replace MarkUserResource with a global resource.
class MarkUserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['username', 'first_name', 'last_name', 'last_login', ]
        allowed_methods = ['get', ]

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<username>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

# Displays all marks, with all linked resources exposed by api end-points.
# TODO restrict access to this feature
class MarkResource(ModelResource):
    given_by = fields.ForeignKey(MarkUserResource, 'given_by') 
    last_changed_by = fields.ForeignKey(MarkUserResource, 'last_changed_by')
    given_to = fields.ToManyField(MarkUserResource, 'given_to')

    class Meta:
        queryset = Mark.objects.all()
        resource_name = 'marks/marks'

# Shows all of a loggedi n users entries. This only exposes api end-points, and is the
# preferred way of fetching your ammount of marks.
class EntryResource(ModelResource):
    user = fields.ToOneField(MarkUserResource, 'user')
    mark = fields.ToOneField(MarkResource, 'mark')

    class Meta:
        queryset = UserEntry.objects.all()
        resource_name = 'marks/entry'
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()

    def obj_create(self, bundle, request=None, **kwargs):
        return super(UserLookupResource, self).obj_create(bundle, request, user=request.user)

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(user=request.user)

# Will display a users marks, including all info except the "given_to" part, as this is
# redundant for this api call and could possibly create a loop.
class MyMarksResource(ModelResource):
    given_by = fields.ForeignKey(MarkUserResource, 'given_by') 
    last_changed_by = fields.ForeignKey(MarkUserResource, 'last_changed_by')

    class Meta:
        queryset = Mark.objects.all()
        resource_name = 'marks/mine'

    def obj_create(self, bundle, request=None, **kwargs):
        return super(MyMarksResource, self).obj_create(bundle, request, given_to=request.user)

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(given_to=request.user)
