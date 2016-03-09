# -*- coding: utf-8 -*-
from apps.companyprofile.models import Company
from apps.dashboard.widgets import widget_generator
from apps.gallery.widgets import SingleImageInput
from django.forms import ModelForm


class CompanyForm(ModelForm):

    class Meta(object):
        model = Company
        fields = ('name', 'short_description', 'long_description', 'image', 'site', 'email_address', 'phone_number',)
        exclude = ['old_image']

        # Widget generator accepts a form widget, and a list of tuples between field name and an attribute dict
        widgets = widget_generator(SingleImageInput, [('image', {'id': 'responsive-image-id'})])
