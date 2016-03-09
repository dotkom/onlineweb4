# -*- coding: utf-8 -*-

from apps.marks.models import Mark
from django import forms


class MarkForm(forms.ModelForm):

    class Meta(object):
        model = Mark
        fields = ['title', 'description', 'category']
