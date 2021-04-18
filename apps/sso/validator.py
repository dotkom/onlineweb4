from oauth2_provider.oauth2_validators import OAuth2Validator

from .userinfo import Onlineweb4Userinfo


class Validator(OAuth2Validator):
    """
    A custom validator allows us to extend claims for the idtoken and the /userinfo-endpoint.
    https://django-oauth-toolkit.readthedocs.io/en/latest/oidc.html#customizing-the-oidc-responses
    """

    def get_additional_claims(self, request):
        # https://openid.net/specs/openid-connect-core-1_0.html#ScopeClaims
        claims = {}
        user = request.user
        if "profile" in request.scopes:
            claims["name"] = user.get_full_name()
            claims["given_name"] = user.first_name
            claims["family_name"] = user.last_name
            claims["nickname"] = user.nickname
            claims["website"] = user.website
            claims["picture"] = user.get_image_url()
            claims["preferred_username"] = user.username

        if "email" in request.scopes:
            claims["email"] = user.primary_email
            claims["email_verified"] = user.email_object.verified

        if "address" in request.scopes:
            claims["address"] = {}
            claims["address"]["formatted"] = f"{user.address}, {user.zip_code}"
            claims["address"]["street_address"] = user.address
            claims["address"]["postal_code"] = user.zip_code

        if "phone" in request.scopes:
            claims["phone_number"] = user.phone_number
            claims[
                "phone_number_verified"
            ] = False  # None of our phone numbers are verified.
        if "online" in request.scopes:
            online_related_claims = Onlineweb4Userinfo(user).oidc()
            claims = {**online_related_claims, **claims}
        return claims

    def get_userinfo_claims(self, request):
        claims = super().get_userinfo_claims(request)
        return claims
