from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import Http404
from rest_framework import exceptions, metadata, viewsets
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
        for method in {"PUT", "POST"} & set(view.allowed_methods):
            action = view.action_map.get(method.lower())
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
                serializer = view.get_serializer_class_by_action(action)
                actions[method] = self.get_serializer_info(serializer())
            finally:
                view.request = request
        return actions


class MultiSerializerMixin(viewsets.GenericViewSet):
    """
    Allows for defining a serializer for each type of action in a viewset.
    """

    # Map of actions to serializer classes
    serializer_classes = None
    metadata_class = ActionMeta

    def __init__(self, *args, **kwargs):
        if self.serializer_classes is None:
            raise ImproperlyConfigured(
                "Multi serializer viewsets have to define a map of serializers. "
                "Define either the 'serializer_classes' dict with an action mapping to each serializer."
            )
        super().__init__(*args, **kwargs)

    def get_serializer_class_by_action(self, action: str):
        """
        Get the serializer matching the current action.
        """
        # Use either the configured 'default' in the map, or use the standard serializer_class like regular viewsets
        default_class = self.serializer_classes.get("default", self.serializer_class)

        # Use specialized default shorthands for read or write actions.
        if self.request.method in ["GET"]:
            default_class = self.serializer_classes.get("read", default_class)
        if self.request.method in ["POST", "PUT", "PATCH"]:
            default_class = self.serializer_classes.get("write", default_class)

        # Get the specific serializer matching the used action with the fallback specified above.
        return self.serializer_classes.get(action, default_class)

    def get_serializer_class(self):
        serializer_class = self.get_serializer_class_by_action(self.action)
        return serializer_class if serializer_class else super().get_serializer_class()
