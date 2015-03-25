# -*- coding: utf-8 -*-

from django import forms

from apps.posters.models import Poster


class AddPosterForm(forms.ModelForm):
    when = forms.CharField(label=u"Når", widget=forms.TextInput(attrs={'type': 'datetime-local'}))
    display_from = forms.CharField(label=u"Vis fra", widget=forms.TextInput(attrs={'type': 'date'}))
    display_to = forms.CharField(label=u"Vis til", widget=forms.TextInput(attrs={'type': 'date'}))
    class Meta:
        model = Poster
        fields = ['title', 'company', 'location', 'when', 'category', 'amount', 'description', 
                  'price', 'display_from', 'display_to', 'comments']

class EditPosterForm(forms.ModelForm):
    
    class Meta:
        model = Poster
        fields = ['title', 'company', 'location', 'when', 'category', 'amount', 'description', 
                  'price', 'display_to', 'display_from', 'comments', 'finished']
