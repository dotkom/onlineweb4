# -*- coding: utf-8 -*-
from django.forms import ModelForm
from django.utils.translation import ugettext as _

from apps.companyprofile.models import Company
from apps.gallery.widgets import SingleImageInputMixin


class CompanyForm(ModelForm):

    class Meta(SingleImageInputMixin):
        image_field_name = 'image'
        model = Company
        exclude = ['old_image']
