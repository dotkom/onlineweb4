from django.utils.translation import ugettext as _
from oidc_provider.lib.claims import ScopeClaims

from apps.online_oidc_provider.userinfo import Onlineweb4Userinfo


def userinfo(claims, user):
    """
    Default userinfo view for OpenID Connect.
    Adds full name and picture from Django and OW4.
    """
    # Profile scope
    claims["name"] = user.get_full_name()
    claims["picture"] = user.get_image_url()
    claims["preferred_username"] = user.username

    # Email scope
    claims["email"] = user.primary_email
    claims["email_verified"] = user.email_object.verified

    # Address scope
    claims["address"]["formatted"] = "{}, {}".format(user.address, user.zip_code)
    claims["address"]["street_address"] = user.address
    claims["address"]["postal_code"] = user.zip_code

    # Phone scope
    claims["phone_number"] = user.phone_number
    claims["phone_number_verified"] = False  # None of our phone numbers are verified.

    return claims


class Onlineweb4ScopeClaims(ScopeClaims):

    info_onlineweb4 = (
        _("Onlineweb4"),
        _(
            "Informasjon om brukerprofilen din på online.ntnu.no, "
            "medlemskapet ditt i Online og din studieretning."
        ),
    )

    def scope_onlineweb4(self):
        return Onlineweb4Userinfo(self.user).oidc()

    info_nibble = (_("Nibble"), _("Informasjon om dine kjøp og saldo på Nibble"))

    def scope_nibble(self):
        return {"test": "this data was returned"}
