# -*- coding: utf-8 -*-
from django.forms import ModelForm, HiddenInput
from django.utils.translation import ugettext as _

from apps.companyprofile.models import Company


class CompanyForm(ModelForm):
    
    class Meta(object):
        model = Company
