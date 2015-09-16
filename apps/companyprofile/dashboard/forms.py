# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext as _

from apps.companyprofile.models import Company


class CompanyForm(forms.ModelForm):
    
    class Meta(object):
        model = Company

