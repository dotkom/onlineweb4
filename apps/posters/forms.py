# -*- coding: utf-8 -*-

from django import forms

from apps.posters.models import Poster, GeneralOrder


class AddForm(forms.ModelForm):
    required_css_class = 'required'
    # @ToDo: Look at using event field as datalist
    description = forms.CharField(label='Plakattekst', required=False, widget=forms.Textarea(attrs={'placeholder': 'Detaljert hva du vil ha av tekst på plakaten'}))
    comments = forms.CharField(label='Kommentarer', required=False, widget=forms.Textarea(attrs={'placeholder': 'Eventuell informasjon, kommentarer, lenker til bilder, osv...'}))
    price = forms.IntegerField(label='Pris', required=False, widget=forms.NumberInput(attrs={'placeholder': 'Pris på event'}))
    amount = forms.IntegerField(label='Antall', required=False, widget=forms.NumberInput(attrs={'placeholder': 'Hvor mange vil du ha?', "value" : "10"}))
    display_from = forms.DateField(label=u"Vis plakat fra", required=False, widget=forms.TextInput(attrs={'type': 'date'}))
    
    class Meta:
        model = Poster
        fields = ['event', 'amount', 'description',
                  'price', 'comments']


class AddPosterForm(AddForm):
    #display_to = forms.DateField(label=u"Vis plakat til", required=False,  widget=forms.TextInput(attrs={'type': 'date'}))
    bong = forms.IntegerField(label='Bonger', required=False, widget=forms.NumberInput(attrs={'placeholder': 'Antall bonger du vil ha. La feltet stå tomt hvis du ikke ønsker noen.'}))

    class Meta:
        model = Poster
        fields = ['event', 'amount', 'bong', 'description',
                  'price', 'display_from', 'comments']


class AddBongForm(AddForm):
    pass


class AddOtherForm(AddForm):
    class Meta:
        model = GeneralOrder
        fields = ['title', 'amount', 'price', 'description',
                  'display_from', 'comments']


class EditPosterForm(AddPosterForm):
    class Meta:
        model = Poster
        fields = ['event', 'amount', 'bong', 'description',
                  'price', 'display_to', 'display_from', 'comments', 'finished']


class EditOtherForm(AddPosterForm):
    class Meta:
        model = GeneralOrder
        fields = ['title', 'amount', 'price', 'description',
                  'display_from', 'comments', 'finished']
