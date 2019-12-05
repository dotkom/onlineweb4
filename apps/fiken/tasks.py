import json
import logging

import requests
from onlineweb4.celery import app

from .models import FikenCustomer, FikenSale, FikenSaleAttachment
from .serializers import (
    FikenCustomerSerializer,
    FikenSaleAttachmentSerializer,
    FikenSaleSerializer,
    FikenTransactionFeeSerializer,
)
from .settings import FIKEN_AUTH, FIKEN_ORG_API_URL, IS_FIKEN_CONFIGURED

logger = logging.getLogger(__name__)


def get_fiken_sales_api_url():
    return f"{FIKEN_ORG_API_URL}/sales"


def get_fiken_sales_attachments_api_url(sale_fiken_id: int):
    return f"{get_fiken_sales_api_url()}/{sale_fiken_id}/attachments"


def get_fiken_sales_payment_api_url(sale_fiken_id: int):
    return f"{get_fiken_sales_api_url()}/{sale_fiken_id}/payments"


def get_fiken_customer_api_url():
    return f"{FIKEN_ORG_API_URL}/contacts"


def resolve_fiken_id(location_url: str) -> int:
    return int(location_url.split("/")[-1])


def register_customer_in_fiken(customer_id: int):
    logger.info(f"Starting Fiken customer registration task")
    customer: FikenCustomer = FikenCustomer.objects.get(pk=customer_id)

    if IS_FIKEN_CONFIGURED:
        headers = {"Content-type": "application/json", "Accept": "application/json"}

        customer_data = FikenCustomerSerializer(customer).data

        response = requests.post(
            url=get_fiken_customer_api_url(),
            auth=FIKEN_AUTH,
            headers=headers,
            json=customer_data,
        )

        if response.ok:
            logger.info(
                f"Successfully created customer {customer.id} for user {customer.user}"
            )
            fiken_id = resolve_fiken_id(response.headers.get("Location"))
            customer.refresh_from_db()
            if not customer.fiken_customer_number:
                customer.fiken_customer_number = fiken_id
                customer.save()
            else:
                logger.warning(
                    f"Fiken customer {customer} registered twice with IDs {fiken_id} and"
                    f"{customer.fiken_customer_number}"
                )

        else:
            logger.warning(f"Failed at registering customer {customer.id} in Fiken")
            logger.warning(
                f"Fiken request failed with status code: {response.status_code} and "
                f"message {response.text}"
            )
    else:
        logger.warning(
            f"Fiken is not configured correctly. Could not register customer {customer.id}"
        )


@app.task(bind=True)
def create_sale_attachment(_, sale_id: int):
    logger.info(f"Starting Fiken attachment task")
    sale = FikenSale.objects.get(pk=sale_id)
    attachment: FikenSaleAttachment = sale.create_attachment()
    if IS_FIKEN_CONFIGURED:
        headers = {}

        sale_attachment_data = FikenSaleAttachmentSerializer(attachment).data
        attachment_data = dict(
            SaleAttachment=(None, json.dumps(sale_attachment_data), "application/json"),
            AttachmentFile=(
                attachment.filename,
                attachment.file.read(),
                "application/pdf",
            ),
        )

        response = requests.post(
            url=get_fiken_sales_attachments_api_url(sale.fiken_id),
            auth=FIKEN_AUTH,
            headers=headers,
            files=attachment_data,
        )

        if response.ok:
            logger.info(
                f"Successfully created attachment {attachment.id} for sale {sale.identifier} in Fiken"
            )
        else:
            logger.warning(f"Failed at registering attachment {attachment.id} in Fiken")
            logger.warning(
                f"Fiken request failed with status code: {response.status_code} and "
                f"message {response.text}"
            )
    else:
        logger.warning(
            f"Fiken is not configured correctly. Could not register sale attachment {attachment.id}"
        )


@app.task(bind=True)
def register_stripe_fee_payment(_, sale_id: int):
    sale = FikenSale.objects.get(pk=sale_id)
    logger.info(f"Starting register fee payment task for Sale {sale}")
    fee_payment_data = FikenTransactionFeeSerializer(sale).data

    if IS_FIKEN_CONFIGURED:

        response = requests.post(
            url=get_fiken_sales_payment_api_url(sale.fiken_id),
            auth=FIKEN_AUTH,
            headers={},
            json=fee_payment_data,
        )

        if response.ok:
            logger.info(
                f"Successfully registered fee payment for {sale.identifier} in Fiken"
            )
        else:
            logger.warning(
                f"Failed at registering fee payment for {sale.identifier} in Fiken"
            )
            logger.warning(
                f"Fiken request failed with status code: {response.status_code} and "
                f"message {response.text}"
            )
    else:
        logger.warning(
            f"Fiken is not configured correctly. Could not register fee payment for {sale.identifier}"
        )


@app.task(bind=True)
def register_sale_with_fiken(_, sale_id: int):
    logger.info("Starting Fiken sale register")
    sale = FikenSale.objects.get(pk=sale_id)
    sale_data = FikenSaleSerializer(sale).data

    if IS_FIKEN_CONFIGURED:
        headers = {"Content-type": "application/json", "Accept": "application/json"}

        response = requests.post(
            url=get_fiken_sales_api_url(),
            auth=FIKEN_AUTH,
            headers=headers,
            json=sale_data,
        )

        if response.ok:
            logger.info(f"Successfully registered sale {sale.identifier} in Fiken")
            sale_fiken_id = resolve_fiken_id(response.headers.get("Location"))
            sale.fiken_id = sale_fiken_id
            sale.save()
            register_stripe_fee_payment.delay(sale_id=sale.id)
            create_sale_attachment.delay(sale_id=sale_id)
        else:
            logger.warning(f"Failed at registering sale {sale.identifier} in Fiken")
            logger.warning(
                f"Fiken request failed with status code: {response.status_code} and "
                f"message {response.text}"
            )
    else:
        logger.warning(
            f"Fiken is not configured correctly. Could not register sale {sale.identifier}"
        )
