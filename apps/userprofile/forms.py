# -*- coding: utf-8 -*-

from apps.userprofile.models import Privacy
from django import forms
from django.utils.translation import ugettext_lazy as _


class ProfileForm(forms.Form):

    hidden_checkbox_widget = forms.CheckboxInput(attrs={'id' : 'hidden-input'})
    email = forms.EmailField(required=True, error_messages={'required' : _(u"Feltet er påkrevd")}, label="E-post-adresse")
    nickname = forms.CharField(max_length=50, required=False, label="Nickname")
    website = forms.CharField(max_length=50, required=False, label="Webside")
    phone_number = forms.CharField(max_length=20, required=False, label="Telefonnummer")
    address = forms.CharField(max_length=30, required=False, label="Adresse")
    area_code = forms.CharField(max_length=4, required=False, label="Postnummer")
    allergies = forms.CharField(widget=forms.Textarea(attrs={'id' : 'allergies' }), required=False, label="Allergier")
    image_upload = forms.ImageField(widget=forms.FileInput(attrs={'id' : 'hidden-input'}), required=False, label="image")
    infomail = forms.BooleanField(required=False, label="Ønsker infomail")
    mark_rules = forms.BooleanField(required=False, label="Godtatt prikkeregler")


def create_profile_form(userprofile):
    return ProfileForm(initial = {
            'infomail' : userprofile.infomail,
            'address' : userprofile.address,
            'area_code' : userprofile.area_code,
            'allergies' : userprofile.allergies,
            'mark_rules' : userprofile.mark_rules,
            'image' : userprofile.image,
            'nickname' : userprofile.nickname,
            'website' : userprofile.website,
            'email' : userprofile.user.email,
            'phone_number' : userprofile.phone_number
        })


class PrivacyForm(forms.ModelForm):

    class Meta:
        model = Privacy
        exclude = ['user']