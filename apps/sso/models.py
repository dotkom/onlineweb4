# -*- coding: utf8 -*-
#
# Created by 'myth' on 6/25/15

from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _
from oauth2_provider.models import AbstractApplication


class Client(AbstractApplication):
    """
    The Client model is an extension of the Django Oauth Toolkits basic Application model (Client)
    We need to subclass it and use django model swapping functionality to support predefined
    scopes on a per-client basis.
    """

    scopes = models.TextField(verbose_name=_("Tilganger"), blank=True)
    website_url = models.TextField(blank=True)
    terms_url = models.TextField(blank=True)
    logo = models.ImageField(
        blank=True, default="", upload_to="oauth2_provider/clients"
    )
    contact_email = models.TextField(blank=True)

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

        self.scopes = " ".join(scopes)

    class Meta:
        permissions = (("view_client", "View Client"),)
        default_permissions = ("add", "change", "delete")


class ApplicationConsent(models.Model):
    """
    The Application Consent is an alternative to django-oidc-providers UserConsent,
    a list of which applications you have previously granted access to, and which accesses was given.
    This is useful in the case where an external application saves your data, and you would like to know
    which ones you have given access to.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_(u"User"), on_delete=models.CASCADE
    )
    date_given = models.DateTimeField(auto_now_add=True, verbose_name=_(u"Date Given"))
    client = models.ForeignKey(
        Client, on_delete=models.PROTECT
    )  # Prevent client deletions to always allow users to know where their data may have gone.
    approved_scopes = models.TextField(verbose_name=_("Tilganger"), blank=True)

    def get_approved_scopes(self):
        """
        Returns the scopes field as an iterable
        :return: A list of scope strings
        """

        return self.approved_scopes.split()

    def set_approved_scopes(self, approved_scopes):
        """
        Sets the scopes field from an iterable
        :param scopes: A list of scope strings
        """

        self.approved_scopes = " ".join(approved_scopes)

    class Meta:
        unique_together = ("user", "client")
