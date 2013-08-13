# -*- coding: utf-8 -*-

from django import forms

class ProfileForm(forms.Form):

    email = forms.EmailField()
    nickname = forms.CharField(max_length=50)
    website = forms.CharField(max_length=50)
    phone_number = forms.CharField(max_length=20)
    address = forms.CharField(max_length=30)
    area_code = forms.CharField(max_length=4)
    allergies = forms.CharField(widget=forms.Textarea(attrs={'id' : 'allergies' }))
    image_upload = forms.ImageField(widget=forms.FileInput(attrs={'id' : 'hidden-input'}))
    infomail = forms.BooleanField()
    mark_rules = forms.BooleanField()