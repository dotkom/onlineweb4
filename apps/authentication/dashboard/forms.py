from django import forms
from guardian.shortcuts import get_objects_for_user

from apps.authentication.models import OnlineGroup
from apps.dashboard.widgets import multiple_widget_generator
from apps.gallery.widgets import SingleImageInput


class OnlineGroupForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["parent_group"].queryset = get_objects_for_user(
            user=user, perms="authentication.change_onlinegroup", klass=OnlineGroup
        )

    class Meta:
        model = OnlineGroup
        fields = [
            "parent_group",
            "name_short",
            "name_long",
            "description_short",
            "description_long",
            "email",
            "group_type",
            "roles",
            "admin_roles",
            "image",
        ]

        # Fields should be a mapping between field name and an attribute dictionary
        img_fields = [("image", {"id": "responsive-image-id"})]
        widgetlist = [(SingleImageInput, img_fields)]

        # Multiple widget generator merges results from regular widget_generator into a single widget dict
        widgets = multiple_widget_generator(widgetlist)
