from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from .models import OnlineUser


class Auth0OIDCAB(OIDCAuthenticationBackend):
    def filter_users_by_claims(self, claims):
        sub = claims.get("sub")
        if not sub:
            return self.UserModel.objects.none()

        try:
            user = OnlineUser.objects.get(auth0_subject=sub)
            return [user]

        except OnlineUser.DoesNotExist:
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
