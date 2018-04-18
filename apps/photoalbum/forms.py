# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext as _

from apps.photoalbum.models import Album

class ReportPhotoForm(forms.Form):
	reason = forms.CharField(widget=forms.TextInput(), label=_("Begrunnelse"))
