from rest_framework import permissions, viewsets


class ModelPermission(permissions.BasePermission):
    """
    Extendable Permission class for DRF.
    Allows viewing by anyone.
    Restricts creating, updating and deleting to custom permissions.
    """

    """ Override values to set permissions on a view """
    view_permissions = []
    update_permissions = []
    create_permissions = []
    delete_permissions = []

    def _check_permissions(self, user, perms, obj = None):
        if len(perms) == 0:
            return True
        if user.is_authenticated:
            for permission in perms:
                if not obj:
                    if user.has_perm(permission):
                        return True
                else:
                    if user.has_perm(permission, obj):
                        return True
        return False
    
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if view.action in ['list', 'retrieve']:
            return self._check_permissions(request.user, self.view_permissions)

        elif view.action in ['update', 'partial_update']:
            return self._check_permissions(request.user, self.update_permissions)

        elif view.action in ['create']:
            return self._check_permissions(request.user, self.create_permissions)

        elif view.action in ['destroy']:
            return self._check_permissions(request.user, self.delete_permissions)

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        # Deny actions on objects if the user is not authenticated
        if not request.user.is_authenticated:
            return False

        if view.action in ['retrieve']:
            return self._check_permissions(request.user, self.view_permissions, obj)

        elif view.action in ['update', 'partial_update']:
            return self._check_permissions(request.user, self.update_permissions, obj)

        elif view.action in ['destroy']:
            return self._check_permissions(request.user, self.delete_permissions, obj)

        return False
