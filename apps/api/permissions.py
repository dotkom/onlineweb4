from oauth2_provider.contrib.rest_framework import TokenHasScope
from rest_framework.permissions import DjangoModelPermissions, DjangoObjectPermissions

_perms_map_with_view_perms = {
    "GET": ["%(app_label)s.view_%(model_name)s"],
    "OPTIONS": [],
    "HEAD": [],
    "POST": ["%(app_label)s.add_%(model_name)s"],
    "PUT": ["%(app_label)s.change_%(model_name)s"],
    "PATCH": ["%(app_label)s.change_%(model_name)s"],
    "DELETE": ["%(app_label)s.delete_%(model_name)s"],
}


class TokenHasScopeOrUserHasObjectPermissionsOrWriteOnly(
    DjangoObjectPermissions, TokenHasScope
):
    perms_map = _perms_map_with_view_perms

    def has_permission(self, request, view):
        if request.method == "POST":
            return True

        return super().has_permission(request, view)


class TokenHasScopeOrUserHasModelPermissionsOrWriteOnly(
    DjangoModelPermissions, TokenHasScope
):
    perms_map = _perms_map_with_view_perms

    def has_permission(self, request, view):
        if request.method == "POST":
            return True

        return super().has_permission(request, view)
