# -*- coding: utf-8 -*-

from django import forms

from apps.posters.models import Poster


class AddPosterForm(forms.ModelForm):
    display_from = forms.CharField(label=u"Vis plakat fra", widget=forms.TextInput(attrs={'type': 'date'}))
    display_to = forms.CharField(label=u"Vis plakat til", widget=forms.TextInput(attrs={'type': 'date'}))
    class Meta:
        model = Poster
        fields = ['event', 'amount', 'description',
                  'price', 'display_from', 'display_to', 'comments']

class EditPosterForm(forms.ModelForm):
    
    class Meta:
        model = Poster
        fields = ['event', 'amount', 'description',
                  'price', 'display_to', 'display_from', 'comments', 'finished']
