# -*- coding: utf-8 -*-
from django import forms

from apps.dashboard.widgets import widget_generator
from apps.gallery.widgets import SingleImageInput
from apps.inventory.models import Batch, Item, ItemCategory


class ItemForm(forms.ModelForm):

    class Meta(object):
        model = Item
        fields = ('name', 'description', 'category', 'available', 'price', 'image')

        # Widget generator accepts a form widget, and a list of tuples between field name and an attribute dict
        widgets = widget_generator(SingleImageInput, [('image', {'id': 'responsive-image-id'})])


class CategoryForm(forms.ModelForm):

    class Meta(object):
        model = ItemCategory
        fields = ('name', )


class BatchForm(forms.ModelForm):

    class Meta(object):
        model = Batch
        exclude = ['item']
