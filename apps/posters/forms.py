# -*- coding: utf-8 -*-

from django import forms

from apps.posters.models import Poster


class AddForm(forms.ModelForm):
    required_css_class = 'required'
    # @ToDo: Look at using event field as datalist
    description = forms.CharField(label='Beskrivelse', required=True, widget=forms.Textarea(attrs={'placeholder': 'Detaljert beskrivelse av det som bestilles'}))
    comments = forms.CharField(label='Kommentarer', required=False, widget=forms.Textarea(attrs={'placeholder': 'Ekstra info om bestillingen, og evt. antall bonger'}))
    price = forms.IntegerField(label='Pris', required=False, widget=forms.NumberInput(attrs={'placeholder': 'Pris på event'}))
    amount = forms.IntegerField(label='Antall', required=False, widget=forms.NumberInput(attrs={'placeholder': 'Hvor mange vil du ha?'}))

    class Meta:
        model = Poster
        fields = ['event', 'amount', 'description',
                  'price', 'comments']


class AddPosterForm(AddForm):
    display_from = forms.CharField(label=u"Vis plakat fra", required=False, widget=forms.TextInput(attrs={'type': 'date'}))
    display_to = forms.CharField(label=u"Vis plakat til", required=False,  widget=forms.TextInput(attrs={'type': 'date'}))

    class Meta:
        model = Poster
        fields = ['event', 'amount', 'description',
                  'price', 'display_from', 'display_to', 'comments']


class AddBongForm(AddForm):
    pass


class AddOtherForm(AddForm):
    pass


class EditPosterForm(AddForm):
    class Meta:
        model = Poster
        fields = ['event', 'amount', 'description',
                  'price', 'display_to', 'display_from', 'comments', 'finished']
