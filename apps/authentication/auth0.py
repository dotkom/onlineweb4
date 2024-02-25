from auth0.authentication import GetToken
from auth0.management import Auth0
from django.conf import settings


def auth0_client():
    domain = settings.AUTH0_DOMAIN

    get_token = GetToken(
        domain,
        settings.AUTH0_CLIENT_ID,
        client_secret=settings.AUTH0_CLIENT_SECRET,
    )
    token = get_token.client_credentials(f"https://{domain}/api/v2/")
    mgmt_api_token = token["access_token"]

    return Auth0(domain, mgmt_api_token)
