from django.conf import settings
from requests.auth import HTTPBasicAuth

FIKEN_API_URL = 'https://fiken.no/api/v1'
FIKEN_USER = settings.OW4_FIKEN_USER
FIKEN_PASSWORD = settings.OW4_FIKEN_PASSWORD
FIKEN_AUTH = HTTPBasicAuth(FIKEN_USER, FIKEN_PASSWORD)
FIKEN_ORG = settings.OW4_FIKEN_ORG
FIKEN_ORG_API_URL = f'{FIKEN_API_URL}/companies/{FIKEN_ORG}'

IS_FIKEN_CONFIGURED = FIKEN_USER and FIKEN_PASSWORD and FIKEN_ORG

NIBBLE_ACCOUNT_NAME = 'nibble'
