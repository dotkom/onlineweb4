from rest_framework.permissions import DjangoModelPermissions, DjangoObjectPermissions

restricted_view_perms_map = {
    "GET": ["%(app_label)s.view_%(model_name)s"],
    "OPTIONS": [],
    "HEAD": [],
    "POST": ["%(app_label)s.add_%(model_name)s"],
    "PUT": ["%(app_label)s.change_%(model_name)s"],
    "PATCH": ["%(app_label)s.change_%(model_name)s"],
    "DELETE": ["%(app_label)s.delete_%(model_name)s"],
}


class RestrictedModelPermission(DjangoModelPermissions):
    perms_map = restricted_view_perms_map


class RestrictedObjectPermission(DjangoObjectPermissions):
    perms_map = restricted_view_perms_map
