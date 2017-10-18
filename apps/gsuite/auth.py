from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


def generate_g_suite_credentials(json_keyfile_name=settings.OW4_GSUITE_SYNC.get('CREDENTIALS'), scopes=list()):
    """
    Creates the credentials required for building a Google API Client Resource.
    :param json_keyfile_name: Path to the JSON keyfile. Get this at
        https://console.developers.google.com/apis/credentials?project=ow4-gsuitesync
    :type json_keyfile_name: str
    :param scopes: A list of scopes that the Service Account should be able to access.
    :type scopes: list
    :return: Credentials
    :rtype: ServiceAccountCredentials
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile_name, scopes=scopes)
    credentials = credentials.create_delegated(settings.OW4_GSUITE_SETTINGS.get('DELEGATED_ACCOUNT'))

    return credentials


def build_g_suite_service(service, version, credentials):
    """
    Builds a Google API Resource Client.
    :param service: The service to get a client for.
    :type service: str
    :param version: The version of the service to get a client for.
    :type version: str
    :param credentials: The credentials used to gain access to the API Resource.
    :type credentials: oauth2client.client.GoogleCredentials
    :return: A Google API Resource Client
    """
    if not credentials:
        raise ValueError('Missing credentials for G Suite API service!')

    if not settings.OW4_GSUITE_SETTINGS.get('ENABLED', False):
        raise ImproperlyConfigured('Enable G Suite Syncer in OW4 settings to be able to use it.')

    # Example of build: build('admin', 'directory_v1', credentials=credentials)
    return build(service, version, credentials=credentials)


def build_and_authenticate_g_suite_service(service, version, scopes,
                                           json_keyfile_name=settings.OW4_GSUITE_SETTINGS.get('CREDENTIALS')):
    """
    Method which combines building and authenticating a Client towards the Google API.
    :param service: The service to get a client for.
    :type service: str
    :param version: The version of the service to get a client for.
    :type version: str
    :param scopes: A list of scopes that the Service Account should be able to access.
    :type scopes: list
    :param json_keyfile_name: Path to the JSON keyfile. Get this at
        https://console.developers.google.com/apis/credentials?project=ow4-gsuitesync
    :type json_keyfile_name: str
    :return: A Google API Resource Client
    """
    credentials = generate_g_suite_credentials(json_keyfile_name=json_keyfile_name, scopes=scopes)
    return build_g_suite_service(service, version, credentials)
