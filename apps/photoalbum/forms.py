# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext as _


class ReportPhotoForm(forms.Form):
    reason = forms.CharField(widget=forms.TextInput(), label=_("Begrunnelse"))
