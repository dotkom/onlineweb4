# -*- coding: utf-8 -*-
from django.forms import ModelForm
from django.utils.translation import ugettext as _

from apps.companyprofile.models import Company
from apps.dashboard.widgets import widget_generator
from apps.gallery.widgets import SingleImageInput


class CompanyForm(ModelForm):

    class Meta(object):
        model = Company
        fields = ('name', 'short_description', 'long_description', 'image', 'site', 'email_address', 'phone_number',)
        exclude = ['old_image']

        # Widget generator accepts a form widget, and a list of tuples between field name and an attribute dict
        widgets = widget_generator(SingleImageInput, [('image', {'id': 'responsive-image-id'})])

