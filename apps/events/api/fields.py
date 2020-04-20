from rest_framework import serializers


class SerializerUserMethodField(serializers.SerializerMethodField):
    """
    Serialize a field related to a user.
    Gets a field from a model instance with only the user as an argument.
    """

    def bind(self, field_name, parent):
        if self.method_name is None:
            self.method_name = field_name
        super().bind(field_name, parent)

    def to_representation(self, obj):
        request = self.context.get("request", None)
        if request:
            get_user_field_method = getattr(obj, self.method_name)
            return get_user_field_method(request.user)
        return None
