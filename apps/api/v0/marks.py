# -*- coding: utf-8 -*-

from tastypie import fields
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.bundle import Bundle
from tastypie.resources import ModelResource

from apps.marks.models import Mark, MarkUser
from apps.api.v0.authentication import UserResource


# TODO restrict access to this feature
class MarkResource(ModelResource):
    """
    Displays all marks, with all linked resources exposed by api end-points.
    """
    given_by = fields.ForeignKey(UserResource, 'given_by')
    last_changed_by = fields.ForeignKey(UserResource, 'last_changed_by')
    given_to = fields.ToManyField(UserResource, 'given_to')

    class Meta:
        queryset = Mark.objects.all()
        resource_name = 'marks/marks'
        excludes = ['id', ]


class EntryResource(ModelResource):
    """
    Shows all the mark entries for an authenticated user.

    This resource exposes only the api end-points, which is the minimal ammount
    of data this api can supply while still listing all marks that belongs to a user.
    """
    user = fields.ToOneField(UserResource, 'user')
    mark = fields.ToOneField(MarkResource, 'mark')

    class Meta:
        queryset = MarkUser.objects.all()
        resource_name = 'marks/entry'
        excludes = ['id', ]
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
    given_by = fields.ForeignKey(UserResource, 'given_by')
    last_changed_by = fields.ForeignKey(UserResource, 'last_changed_by')


    class Meta:
        queryset = Mark.objects.all()
        resource_name = 'marks/mine'
        excludes = ['id', ]
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
    given_by = fields.ForeignKey(UserResource, 'given_by')
    last_changed_by = fields.ForeignKey(UserResource, 'last_changed_by')

    class Meta:
        queryset = Mark.marks.all_active()
        resource_name = 'marks/active'
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()

    def obj_create(self, bundle, request=None, **kwargs):
        return super(MyMarksResource, self).obj_create(bundle, request, given_to=request.user)

    def apply_authorization_lawimits(self, request, object_list):
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
