# -*- coding: utf-8 -*-
from django import forms

from apps.dashboard.widgets import widget_generator
from apps.gallery.widgets import SingleImageInput
from apps.inventory.models import Batch, Item, ItemCategory


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = (
            "name",
            "description",
            "category",
            "available",
            "price",
            "low_stock_treshold",
            "image",
        )

        # Widget generator accepts a form widget, and a list of tuples between field name and an attribute dict
        widgets = widget_generator(
            SingleImageInput, [("image", {"id": "responsive-image-id"})]
        )


class CategoryForm(forms.ModelForm):
    class Meta:
        model = ItemCategory
        fields = ("name",)


class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        exclude = ["item"]
