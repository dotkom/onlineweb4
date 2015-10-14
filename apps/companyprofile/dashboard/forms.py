# -*- coding: utf-8 -*-
from django.forms import ModelForm
from django.utils.translation import ugettext as _

from apps.companyprofile.models import Company
from apps.gallery.widgets import SingleImageField


class CompanyForm(ModelForm):
    
    class Meta(object):
        model = Company
        exclude = ['old_image']
        widget = {
            'image': SingleImageField(attrs={
                'id': 'responsive-image-id',
            })
        }
