import logging

import requests
from django.conf import settings
from onlineweb4.celery import app
from requests.auth import HTTPBasicAuth

FIKEN_API_URL = 'https://fiken.no/api/v1'
FIKEN_USER = settings.OW4_FIKEN_USER
FIKEN_PASSWORD = settings.OW4_FIKEN_PASSWORD
FIKEN_ORG = settings.OW4_FIKEN_ORG
FIKEN_SALES_API_URL = f'{FIKEN_API_URL}/companies/{FIKEN_ORG}/sales'


logger = logging.getLogger(__name__)


@app.task(bind=True)
def register_sale_with_fiken(_, sale_data: dict):
    logger.info('Starting Fiken register')
    sale_identifier = sale_data.get("identifier")
    if FIKEN_USER and FIKEN_PASSWORD and FIKEN_ORG:
        auth = HTTPBasicAuth(FIKEN_USER, FIKEN_PASSWORD)
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        response = requests.post(
            url=FIKEN_SALES_API_URL,
            auth=auth,
            headers=headers,
            json=sale_data,
        )
        if response.ok:
            logger.info(f'Successfully registered sale {sale_identifier} in Fiken')
        else:
            logger.warning(f'Failed at registering sale {sale_identifier} in Fiken')
            logger.warning(f'Fiken request failed with status code: {response.status_code} and '
                           f'message {response.text}')
    else:
        logger.warning(f'Fiken is not configured correctly. Could not register sale {sale_identifier}')
