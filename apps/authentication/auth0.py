from auth0.authentication import GetToken
from auth0.management import Auth0
from django.conf import settings


def auth0_client():
    issuer: str = settings.AUTH0_ISSUER

    get_token = GetToken(
        issuer.removeprefix("https://"),
        settings.AUTH0_CLIENT_ID,
        client_secret=settings.AUTH0_CLIENT_SECRET,
    )
    token = get_token.client_credentials(f"{settings.AUTH0_MGMT_TENANT}/api/v2/")
    mgmt_api_token = token["access_token"]

    return Auth0(issuer.removeprefix("https://"), mgmt_api_token)
