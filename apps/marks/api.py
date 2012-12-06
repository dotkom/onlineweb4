#-*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from tastypie import fields
from tastypie.authentication import Authentication, BasicAuthentication#, SessionAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.bundle import Bundle
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS

from apps.marks.models import Mark, UserEntry

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

# TODO restrict access to this feature
class MarkResource(ModelResource):
    """
    Displays all marks, with all linked resources exposed by api end-points.
    """
    given_by = fields.ForeignKey(MarkUserResource, 'given_by') 
    last_changed_by = fields.ForeignKey(MarkUserResource, 'last_changed_by')
    given_to = fields.ToManyField(MarkUserResource, 'given_to')

    class Meta:
        queryset = Mark.objects.all()
        resource_name = 'marks/marks'

class EntryResource(ModelResource):
    """
    Shows all the mark entries for an authenticated user.

    This resource exposes only the api end-points, which is the minimal ammount
    of data this api can supply while still listing all marks that belongs to a user.
    """
    user = fields.ToOneField(MarkUserResource, 'user')
    mark = fields.ToOneField(MarkResource, 'mark')

    class Meta:
        queryset = UserEntry.objects.all()
        resource_name = 'marks/entry'
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()

    def obj_create(self, bundle, request=None, **kwargs):
        return super(EntryResource, self).obj_create(bundle, request, user=request.user)

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(user=request.user)

class MyMarksResource(ModelResource):
    """
    Lists all of an authenticated users' marks.

    given_to is excluded, both because users should not be able to see this, 
    it's redundant and it avoids loops.
    """
    given_by = fields.ForeignKey(MarkUserResource, 'given_by') 
    last_changed_by = fields.ForeignKey(MarkUserResource, 'last_changed_by')

    class Meta:
        queryset = Mark.objects.all()
        resource_name = 'marks/mine'
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()

    def obj_create(self, bundle, request=None, **kwargs):
        return super(MyMarksResource, self).obj_create(bundle, request, given_to=request.user)

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(given_to=request.user)

    def get_resource_uri(self, bundle_or_obj):
        """
        Overrides the standard uri rendering to expose marks by their proper endpoint.

        Meaning the uri is /marks/marks/id/ instead of /marks/mine/id/
        """
        kwargs = {
            'resource_name': MarkResource._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.pk
        else:
            kwargs['pk'] = bundle_or_obj.id

        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name

        return self._build_reverse_url("api_dispatch_detail", kwargs=kwargs)

class MyActiveMarksResource(ModelResource):
    """
    Supplies a list of an authenticated users' active marks.
    """
    given_by = fields.ForeignKey(MarkUserResource, 'given_by') 
    last_changed_by = fields.ForeignKey(MarkUserResource, 'last_changed_by')

    class Meta:
        queryset = Mark.active.all()
        resource_name = 'marks/active'
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()

    def obj_create(self, bundle, request=None, **kwargs):
        return super(MyMarksResource, self).obj_create(bundle, request, given_to=request.user)

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(given_to=request.user)

    def get_resource_uri(self, bundle_or_obj):
        """
        Overrides the standard uri rendering to expose marks by their proper endpoint.

        Meaning the uri is /marks/marks/id/ instead of /marks/active/id/
        """
        kwargs = {
            'resource_name': MarkResource._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.pk
        else:
            kwargs['pk'] = bundle_or_obj.id

        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name

        return self._build_reverse_url("api_dispatch_detail", kwargs=kwargs)
