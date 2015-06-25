# -*- coding: utf8 -*-
#
# Created by 'myth' on 6/25/15

from django.conf import settings
from django.db.models import *
from django.utils.translation import ugettext as _

from oauth2_provider.models import AbstractApplication


class Client(AbstractApplication):
    """
    The Client model is an extension of the Django Oauth Toolkits basic Application model (Client)
    We need to subclass it and use django model swapping functionality to support predefined
    scopes on a per-client basis.
    """

    scopes = TextField(verbose_name=_(u'Tilganger'), blank=True)

    def get_scopes(self):
        """
        Returns the scopes field as an iterable
        :return: A list of scope strings
        """

        return self.scopes.split()

    def set_scopes(self, scopes):
        """
        Sets the scopes field from an iterable
        :param scopes: A list of scope strings
        """

        self.scopes = ' '.join(scopes)

    class Meta(object):
        permissions = (
            ('view_client', 'View Client'),
        )
