from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from google.oauth2 import service_account
from googleapiclient.discovery import build
from apps.gsuite.models import ServiceAccount
from django.core import serializers
import json


def generate_g_suite_credentials(scopes=list()):
    """
    Creates the credentials required for building a Google API Client Resource.
    https://console.developers.google.com/apis/credentials?project=ow4-gsuitesync
    :param scopes: A list of scopes that the Service Account should be able to access.
    :type scopes: list
    :return: Credentials
    :rtype: ServiceAccountCredentials
    """
    
    try:
        account = ServiceAccount.objects.all()[:1]
        info = serializers.serialize("json", account)
        info = json.loads(info)
        info = info[0]["fields"]
    except:
        info = ""

    credentials = service_account.Credentials.from_service_account_info(
        info, scopes=scopes
    )
    credentials = credentials.with_subject(
        settings.OW4_GSUITE_SETTINGS.get("DELEGATED_ACCOUNT")
    )

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
        raise ValueError("Missing credentials for G Suite API service!")

    if not settings.OW4_GSUITE_SETTINGS.get("ENABLED", False):
        raise ImproperlyConfigured(
            "Enable G Suite Syncer in OW4 settings to be able to use it."
        )

    # Example of build: build('admin', 'directory_v1', credentials=credentials)
    return build(service, version, credentials=credentials)


def build_and_authenticate_g_suite_service(
    service,
    version,
    scopes):
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
    credentials = generate_g_suite_credentials(scopes=scopes)
    return build_g_suite_service(service, version, credentials)
