import logging
import unicodedata
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import logout
from django.core.exceptions import SuspiciousOperation
from josepy.errors import DeserializationError
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from apps.authentication.auth0 import auth0_client

from .models import OnlineUser


def provider_logout(request):
    # this is in accordance with
    # https://auth0.com/docs/authenticate/login/logout/log-users-out-of-auth0#oidc-logout-endpoint-parameters

    if "oidc_id_token" not in request.session:
        # we probably have an old token from previous auth-regime
        # we need to clear their cookies and previous session, which this hopefully will do
        logout(request)
        return f"{settings.BASE_URL}"

    params = {
        "id_token_hint": request.session["oidc_id_token"],
        "client_id": settings.AUTH0_CLIENT_ID,
        "post_logout_redirect_uri": settings.BASE_URL,
        # federated might be relevant if we support FEIDE
    }
    redirect_url = f"{settings.AUTH0_ISSUER}/oidc/logout?{urlencode(params)}"
    return redirect_url


def generate_username(email):
    # Using Python 3 and Django 1.11+, usernames can contain alphanumeric
    # (ascii and unicode), _, @, +, . and - characters. So we normalize
    # it and slice at 150 characters.
    return unicodedata.normalize("NFKC", email)[:150]


LOGGER = logging.getLogger(__name__)


class Auth0OIDCAB(OIDCAuthenticationBackend):
    def get_or_create_user(self, access_token, id_token, payload):
        """Returns a User instance if 1 user is found. Creates a user if not found
        and configured to do so. Returns nothing if multiple users are matched."""

        userinfo = payload
        # payload = parsed id_token
        if userinfo is None:
            # this is modified from the source, since we do not want to call /userinfo on _every_ API-call
            # this is kinda weird to have here, but ensures the access_token is verified in both DRF and elsewhere
            try:
                userinfo = self.verify_token(access_token)
            except DeserializationError:
                LOGGER.debug("Login failed: invalid access token")
                return None

            if "https://online.ntnu.no" not in userinfo.get("aud", []):
                raise SuspiciousOperation(
                    "Wrong audience, this token is not meant for us"
                )

        # user_info = self.get_userinfo(access_token, id_token, payload)
        # claims_verified = self.verify_claims(user_info)
        # if not claims_verified:
        #     msg = "Claims verification failed"
        #     raise SuspiciousOperation(msg)

        users = self.filter_users_by_claims(userinfo)

        if len(users) == 1:
            if id_token is not None:
                return self.update_user(users[0], userinfo)
            else:
                return users[0]
        elif len(users) > 1:
            # In the rare case that two user accounts have the same email address,
            # bail. Randomly selecting one seems really wrong.
            msg = "Multiple users returned"
            raise SuspiciousOperation(msg)
        elif self.get_settings("OIDC_CREATE_USER", True):
            user_info = (
                userinfo
                if id_token is not None
                else self.get_userinfo(access_token, id_token, payload)
            )
            user = self.create_user(user_info)
            return user
        else:
            LOGGER.debug(
                "Login failed: No user with %s found, and " "OIDC_CREATE_USER is False",
                userinfo.get("sub"),
            )
            return None

    def filter_users_by_claims(self, claims):
        sub = claims.get("sub")
        if not sub:
            return self.UserModel.objects.none()

        try:
            user = self.UserModel.objects.get(auth0_subject=sub)
            return [user]

        except self.UserModel.DoesNotExist:
            return self.UserModel.objects.none()

    def create_user(self, claims):
        user = self.UserModel(
            email=claims["email"],
            auth0_subject=claims["sub"],
            is_active=True,
            username=generate_username(claims["email"]),
        )
        user.save()
        auth0 = auth0_client()
        auth0.users.update(
            user.auth0_subject, {"app_metadata": {"ow4_userid": user.pk}}
        )

        return user

    def update_user(self, user: OnlineUser, claims):
        # if email was updated in Auth0-dashboard instead of through OW

        changed = False

        if (email := claims.get("email")) and email != user.email:
            user.email = email
            changed = True

        if (given_name := claims.get("given_name")) and given_name != user.first_name:
            user.first_name = given_name
            changed = True

        if (family_name := claims.get("family_name")) and family_name != user.last_name:
            user.last_name = family_name
            changed = True

        if (gender := claims.get("gender")) and gender != user.gender:
            user.gender = gender
            changed = True

        if changed:
            user.save()

        return super().update_user(user, claims)
