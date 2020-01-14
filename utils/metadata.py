from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import exceptions, metadata
from rest_framework.request import clone_request


class ActionMeta(metadata.SimpleMetadata):
    """
    Metadata class for determining metadata based on the used serializer.
    """

    def determine_actions(self, request, view):
        """
        For generic class based views we return information about
        the fields that are accepted for 'PUT' and 'POST' methods.

        NOTE: This method is based directly on `SimpleMetadata.determine_actions`
        and would need to change if it ever changed.
        """
        actions = {}
        meta_action = view.action
        for method in {"PUT", "POST"} & set(view.allowed_methods):
            view.action = view.action_map.get(method.lower())
            view.request = clone_request(request, method=method)
            try:
                # Test global permissions
                if hasattr(view, "check_permissions"):
                    view.check_permissions(view.request)
                # Test object permissions
                if method == "PUT" and hasattr(view, "get_object"):
                    view.get_object()
            except (exceptions.APIException, PermissionDenied, Http404):
                pass
            else:
                # If user has appropriate permissions for the view, include
                # appropriate metadata about the fields that should be supplied.
                serializer = view.get_serializer()
                actions[method] = self.get_serializer_info(serializer)
            finally:
                view.request = request
                view.action = meta_action
        return actions
