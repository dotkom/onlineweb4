import json
import logging

import requests
from django.conf import settings
from onlineweb4.celery import app
from requests.auth import HTTPBasicAuth

from .models import FikenSale, FikenSaleAttachment
from .serializers import FikenSaleSerializer, FikenSaleAttachmentSerializer

logger = logging.getLogger(__name__)

FIKEN_API_URL = 'https://fiken.no/api/v1'
FIKEN_USER = settings.OW4_FIKEN_USER
FIKEN_PASSWORD = settings.OW4_FIKEN_PASSWORD
FIKEN_ORG = settings.OW4_FIKEN_ORG
IS_FIKEN_CONFIGURED = FIKEN_USER and FIKEN_PASSWORD and FIKEN_ORG


def get_fiken_sales_api_url():
    return f'{FIKEN_API_URL}/companies/{FIKEN_ORG}/sales'


def get_fiken_sales_attachments_api_url(sale_fiken_id: int):
    return f'{get_fiken_sales_api_url()}/{sale_fiken_id}/attachments'


def resolve_sale_fiken_id(location_url: str) -> int:
    return int(location_url.split('/')[-1])


@app.task(bind=True)
def create_sale_attachment(_, sale_id: int):
    logger.info(f'Starting Fiken attachment task')
    sale = FikenSale.objects.get(pk=sale_id)
    attachment: FikenSaleAttachment = sale.create_attachment()
    if IS_FIKEN_CONFIGURED:
        auth = HTTPBasicAuth(FIKEN_USER, FIKEN_PASSWORD)
        headers = {'Content-type': 'multipart/form-data', 'Accept': 'application/json'}

        sale_attachment_data = FikenSaleAttachmentSerializer(attachment).data
        attachment_data = dict(
            SaleAttachment=(None, json.dumps(sale_attachment_data), 'application/json'),
            AttachmentFile=('file.pdf', None, 'application/octet-stream'),
        )

        response = requests.post(
            url=get_fiken_sales_attachments_api_url(sale.fiken_id),
            auth=auth,
            headers=headers,
            files=attachment_data,
        )

        if response.ok:
            logger.info(f'Successfully created attachment {attachment.id} for sale {sale.identifier} in Fiken')
        else:
            logger.warning(f'Failed at registering attachment {attachment.id} in Fiken')
            logger.warning(f'Fiken request failed with status code: {response.status_code} and '
                           f'message {response.text}')
    else:
        logger.warning(f'Fiken is not configured correctly. Could not register sale attachment {attachment.id}')


@app.task(bind=True)
def register_sale_with_fiken(_, sale_id: int):
    logger.info('Starting Fiken sale register')
    sale = FikenSale.objects.get(pk=sale_id)
    sale_data = FikenSaleSerializer(sale).data
    if IS_FIKEN_CONFIGURED:
        auth = HTTPBasicAuth(FIKEN_USER, FIKEN_PASSWORD)
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

        response = requests.post(
            url=get_fiken_sales_api_url(),
            auth=auth,
            headers=headers,
            json=sale_data,
        )

        if response.ok:
            logger.info(f'Successfully registered sale {sale.identifier} in Fiken')
            sale_fiken_id = resolve_sale_fiken_id(response.headers.get('Location'))
            sale.fiken_id = sale_fiken_id
            sale.save()
            create_sale_attachment.delay(sale_id=sale_id)
        else:
            logger.warning(f'Failed at registering sale {sale.identifier} in Fiken')
            logger.warning(f'Fiken request failed with status code: {response.status_code} and '
                           f'message {response.text}')
    else:
        logger.warning(f'Fiken is not configured correctly. Could not register sale {sale.identifier}')
