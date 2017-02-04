from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


def generate_g_suite_credentials(json_keyfile_name=settings.OW4_GSUITE_SYNC.get('CREDENTIALS'), scopes=list()):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile_name, scopes=scopes)
    credentials = credentials.create_delegated(settings.OW4_GSUITE_SYNC.get('DELEGATED_ACCOUNT'))

    return credentials


def build_g_suite_service(service, version, credentials):
    if not credentials:
        raise ValueError('Missing credentials for G Suite API service!')

    if not settings.OW4_GSUITE_SYNC.get('ENABLED', False):
        raise ImproperlyConfigured('Enable G Suite Syncer in OW4 settings to be able to use it.')

    # Example of build: build('admin', 'directory_v1', credentials=credentials)
    return build(service, version, credentials=credentials)


def build_and_authenticate_g_suite_service(service, version, scopes,
                                           json_keyfile_name=settings.OW4_GSUITE_SYNC.get('CREDENTIALS')):
    credentials = generate_g_suite_credentials(json_keyfile_name=json_keyfile_name, scopes=scopes)
    return build_g_suite_service(service, version, credentials)
