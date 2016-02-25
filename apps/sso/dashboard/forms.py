# -*- coding: utf8 -*-
#
# Created by 'myth' on 6/27/15

from django import forms
from django.core.exceptions import ValidationError

from oauth2_provider.settings import oauth2_settings
from oauth2_provider.validators import validate_uris

from apps.sso.models import Client


class NewClientForm(forms.ModelForm):
    """
    The NewClientForm is responsible for rendering forms for creation of new Apps that can access
    user information through OAuth2.
    """

    def clean(self):
        """
        clean override to check the validity of both redirect uri's and scopes
        """
        cleaned_data = super(NewClientForm, self).clean()
        scopes = cleaned_data.get('scopes')
        redirect_uris = cleaned_data.get('redirect_uris')

        # Preliminary check that the data has passed per-field cleaning
        if scopes and redirect_uris:
            # Split the scopes and check that the requested scopes are a subset of the available ones
            scopes_list = scopes.split(' ')
            if not set(scopes_list) <= set([s for s, k in oauth2_settings.user_settings['SCOPES'].items()]):
                self.add_error('scopes', 'Feltet inneholder ugyldige tilganger.')

            # Validate the uris
            try:
                validate_uris(redirect_uris)
            except ValidationError:
                self.add_error('redirect_uris', 'Feltet inneholder ugyldige URIer.')

    class Meta(object):
        """
        Metaclass
        """

        model = Client
        exclude = ['client_id', 'client_secret', 'skip_authorization', 'user']
