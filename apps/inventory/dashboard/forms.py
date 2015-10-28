# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext as _

from apps.inventory.models import Item, Batch

class ItemForm(forms.ModelForm):

    class Meta:
        model = Item
        fields = ('name',)

class BatchForm(forms.ModelForm):

    class Meta:
        model = Batch
        exclude = ['item']
