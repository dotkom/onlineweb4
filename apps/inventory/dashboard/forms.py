# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext as _

from apps.inventory.models import Item, Batch

class InventoryForm(forms.ModelForm):

    class Meta:
        model = Item

class BatchForm(forms.ModelForm):

    class Meta:
        model = Batch
