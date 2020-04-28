from django.core.exceptions import ImproperlyConfigured
from rest_framework import serializers, viewsets

from utils.metadata import ActionMeta


class DefaultDestroySerializer(serializers.Serializer):
    """
    Destroy actions usually don't have a serializer, but for automatic schema generation to work
    all actions need to have a serializer. This is provided as a default for destroy actions
    for openapi schemas to be rendered correctly.
    """

    pass


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
        if action in ["list", "retrieve"]:
            default_class = self.serializer_classes.get("read", default_class)
        if action in ["create", "update", "partial_update"]:
            default_class = self.serializer_classes.get("write", default_class)
            if action == "partial_update":
                default_class = self.serializer_classes.get("update", default_class)
        if action == "destroy":
            default_class = DefaultDestroySerializer

        # Get the specific serializer matching the used action with the fallback specified above.
        return self.serializer_classes.get(action, default_class)

    def get_serializer_class(self):
        serializer_class = self.get_serializer_class_by_action(self.action)
        return serializer_class if serializer_class else super().get_serializer_class()
