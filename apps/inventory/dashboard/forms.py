# -*- coding: utf-8 -*-
from django import forms

from apps.inventory.models import Item, Batch


class ItemForm(forms.ModelForm):

    class Meta(object):
        model = Item
        fields = ('name',)


class BatchForm(forms.ModelForm):

    class Meta(object):
        model = Batch
        exclude = ['item']
