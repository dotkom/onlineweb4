from django import forms

from apps.authentication.models import OnlineGroup
from apps.dashboard.widgets import multiple_widget_generator
from apps.gallery.widgets import SingleImageInput


class OnlineGroupForm(forms.ModelForm):
    class Meta:
        model = OnlineGroup
        fields = [
            "name_short",
            "name_long",
            "description_short",
            "description_long",
            "email",
            "group_type",
            "image",
        ]

        # Fields should be a mapping between field name and an attribute dictionary
        img_fields = [("image", {"id": "responsive-image-id"})]
        widgetlist = [(SingleImageInput, img_fields)]

        # Multiple widget generator merges results from regular widget_generator into a single widget dict
        widgets = multiple_widget_generator(widgetlist)
