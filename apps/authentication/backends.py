from urllib.parse import urlencode

from django.conf import settings
from mozilla_django_oidc.auth import OIDCAuthenticationBackend


def provider_logout(request):
    # this is in accordance with
    # https://auth0.com/docs/authenticate/login/logout/log-users-out-of-auth0#oidc-logout-endpoint-parameters

    params = {
        "id_token_hint": request.session["oidc_id_token"],
        "client_id": settings.AUTH0_CLIENT_ID,
        "post_logout_redirect_uri": settings.BASE_URL,
        # federated might be relevant if we support FEIDE
    }
    redirect_url = f"{settings.AUTH0_DOMAIN}/oidc/logout?{urlencode(params)}"
    return redirect_url


class Auth0OIDCAB(OIDCAuthenticationBackend):
    def filter_users_by_claims(self, claims):
        sub = claims.get("sub")
        if not sub:
            return self.UserModel.objects.none()

        try:
            user = self.UserModel.objects.get(auth0_subject=sub)
            return [user]

        except self.UserModel.DoesNotExist:
            return self.UserModel.objects.none()

    def get_userinfo(self, access_token, id_token, payload):
        userinfo = super().get_userinfo(access_token, id_token, payload)
        # this is here for debug-reasons
        # print(f"{userinfo=}\n{id_token=}\n{access_token=}")
        return userinfo

    def create_user(self, claims):
        # TDOO: implement this
        raise NotImplementedError

    def update_user(self, user, claims):
        return super().update_user(user, claims)
