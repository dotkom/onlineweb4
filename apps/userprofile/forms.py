# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

class ProfileForm(forms.Form):

    email = forms.EmailField(required=True, error_messages={'required' : _(u"Feltet er påkrevd")})
    nickname = forms.CharField(max_length=50, required=False)
    website = forms.CharField(max_length=50, required=False)
    phone_number = forms.CharField(max_length=20, required=False)
    address = forms.CharField(max_length=30, required=False)
    area_code = forms.CharField(max_length=4, required=False)
    allergies = forms.CharField(widget=forms.Textarea(attrs={'id' : 'allergies' }), required=False)
    image_upload = forms.ImageField(widget=forms.FileInput(attrs={'id' : 'hidden-input'}), required=False)
    infomail = forms.BooleanField(required=False)
    mark_rules = forms.BooleanField(required=False)


def createFromUserProfile(userprofile):
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