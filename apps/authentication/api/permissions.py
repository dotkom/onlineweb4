from rest_framework import permissions


class IsSelfOrSuperUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user == obj
        )
