from rest_framework import serializers
from wiki.core import permissions


class WikiPermissionField(serializers.SerializerMethodField):

    def bind(self, field_name, parent):
        if self.method_name is None:
            self.method_name = field_name
        super().bind(field_name, parent)

    def to_representation(self, obj):
        request = self.context.get('request', None)
        if request:
            get_permission = getattr(permissions, self.method_name)
            return get_permission(obj, request.user)
        return None
