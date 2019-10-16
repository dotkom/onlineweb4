# -*- coding: utf-8 -*-
from django.forms import ModelForm
from django.forms.fields import URLField

from apps.companyprofile.models import Company
from apps.dashboard.widgets import widget_generator
from apps.gallery.widgets import SingleImageInput


class CompanyForm(ModelForm):
    site = URLField(max_length=100)

    class Meta:
        model = Company
        fields = ('name', 'short_description', 'long_description', 'image', 'site', 'email_address', 'phone_number',)

        exclude = ['old_image']

        # Widget generator accepts a form widget, and a list of tuples between field name and an attribute dict
        widgets = widget_generator(SingleImageInput, [('image', {'id': 'responsive-image-id'})])
