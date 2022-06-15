from rest_framework import permissions


class DjangoObjectPermissionOrAnonReadOnly(permissions.DjangoObjectPermissions):
    authenticated_users_only = False

    def has_permission(self, request, view):
        if request.method == "POST":
            return super().has_permission(request, view)
        # The rest are handled by object permissions
        return True
