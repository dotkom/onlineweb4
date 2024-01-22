import json
from typing import List, Optional

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from google.auth.credentials import Credentials
from google.oauth2 import service_account
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import Resource, build


def generate_g_suite_credentials(
    json_keyfile_name: str = settings.OW4_GSUITE_SYNC.get("CREDENTIALS"),
    scopes: List[str] = None,
) -> ServiceAccountCredentials:
    """
    Creates the credentials required for building a Google API Client Resource.
    :param json_keyfile_name: Path to the JSON keyfile. Get this at
        https://console.developers.google.com/apis/credentials?project=ow4-gsuitesync
    :param scopes: A list of scopes that the Service Account should be able to access.
    :return: Credentials
    """

    service_account_info = json.load(open(json_keyfile_name))
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info["data"]["data"], scopes=scopes
    )
    credentials = credentials.with_subject(
        settings.OW4_GSUITE_SETTINGS.get("DELEGATED_ACCOUNT")
    )

    return credentials


def build_g_suite_service(
    service: str, version: str, credentials: Optional[Credentials]
) -> Resource:
    """
    Builds a Google API Resource Client.
    :param service: The service to get a client for.
    :param version: The version of the service to get a client for.
    :param credentials: The credentials used to gain access to the API Resource.
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
    service: str,
    version: str,
    scopes: List[str],
    json_keyfile_name: str = settings.OW4_GSUITE_SETTINGS.get("CREDENTIALS"),
) -> Resource:
    """
    Method which combines building and authenticating a Client towards the Google API.
    :param service: The service to get a client for.
    :param version: The version of the service to get a client for.
    :param scopes: A list of scopes that the Service Account should be able to access.
    :param json_keyfile_name: Path to the JSON keyfile. Get this at
        https://console.developers.google.com/apis/credentials?project=ow4-gsuitesync
    :return: A Google API Resource Client
    """
    credentials = generate_g_suite_credentials(
        json_keyfile_name=json_keyfile_name, scopes=scopes
    )
    return build_g_suite_service(service, version, credentials)
