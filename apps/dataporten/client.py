import logging

from oic.oic import Client, RegistrationResponse
from oic.utils.authn.client import CLIENT_AUTHN_METHOD

DATAPORTEN_PROVIDER_CONFIG = 'https://auth.dataporten.no/'


def client_setup(client_id, client_secret):
    """Sets up an OpenID Connect Relying Party ("client") for connecting to Dataporten"""

    logger = logging.getLogger(__name__)

    assert client_id, 'Missing client id when setting up Dataporten OpenID Connect Relying Party'
    assert client_secret, 'Missing client secret when setting up Dataporten OpenID Connect Relying Party'

    client = Client(client_authn_method=CLIENT_AUTHN_METHOD)

    logger.debug('Automatically registering Dataporten OpenID Provider.', extra={'config': DATAPORTEN_PROVIDER_CONFIG})
    client.provider_config(DATAPORTEN_PROVIDER_CONFIG)
    client_args = {
        'client_id': client_id,
        'client_secret': client_secret,
    }
    client.store_registration_info(RegistrationResponse(**client_args))
    logger.debug('Successfully registered the provider.')

    return client
