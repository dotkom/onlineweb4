# -*- coding: utf-8 -*-

import logging

import stripe
from django.utils.translation import gettext as _
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from stripe.error import InvalidRequestError, StripeError

from apps.common.rest_framework.mixins import MultiSerializerMixin
from apps.payment import status as payment_status
from apps.payment.models import (
    PaymentDelay,
    PaymentPrice,
    PaymentRelation,
    PaymentTransaction,
)
from apps.payment.serializers import (
    PaymentDelayReadOnlySerializer,
    PaymentPriceReadOnlySerializer,
    PaymentRelationCreateSerializer,
    PaymentRelationReadOnlySerializer,
    PaymentRelationUpdateSerializer,
    PaymentTransactionCreateSerializer,
    PaymentTransactionReadOnlySerializer,
    PaymentTransactionUpdateSerializer,
)

logger = logging.getLogger(__name__)


class PaymentDelayReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Allow users to view their own payment delays.
    """

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PaymentDelayReadOnlySerializer

    def get_queryset(self):
        user = self.request.user
        return PaymentDelay.objects.filter(user=user)


class PaymentRelationViewSet(MultiSerializerMixin, viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_classes = {
        "read": PaymentRelationReadOnlySerializer,
        "create": PaymentRelationCreateSerializer,
        "update": PaymentRelationUpdateSerializer,
    }

    def get_queryset(self):
        user = self.request.user
        return PaymentRelation.objects.filter(user=user)

    def destroy(self, request, *args, **kwargs):
        """
        Destroy logic is set in the view because serializers cannot delete.
        """
        user = request.user
        payment_relation: PaymentRelation = self.get_object()

        if not payment_relation.is_refundable:
            return Response(
                {"message": payment_relation.is_refundable_reason},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            """Handle the actual refund with the stripe API"""
            stripe.api_key = payment_relation.payment.stripe_private_key
            intent = stripe.PaymentIntent.retrieve(payment_relation.stripe_id)

            if payment_relation.status in [
                payment_status.SUCCEEDED,
                payment_status.DONE,
            ]:
                intent["charges"]["data"][0].refund()

            elif payment_relation.status == payment_status.PENDING:
                intent.cancel()

            elif payment_relation.status in [
                payment_status.REFUNDED,
                payment_status.REMOVED,
            ]:
                return Response(
                    {"message": _("Denne betalingen har allerede blitt refundert.")},
                    status.HTTP_400_BAD_REQUEST,
                )

            payment_relation.refund()
            return Response(
                {"message": _("Betalingen har blitt refundert.")}, status.HTTP_200_OK
            )

        except (InvalidRequestError, StripeError, Exception) as error:
            logger.error(
                f"An error occurred during refund of payment: {payment_relation} "
                f"to stripe for user: {user}",
                error,
            )
            return Response(
                {"message": "Det skjedde en feil under behandlingen av refunderingen"},
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PaymentPriceReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PaymentPriceReadOnlySerializer
    queryset = PaymentPrice.objects.all()


class PaymentTransactionViewSet(MultiSerializerMixin, viewsets.ModelViewSet):
    """
    A user should be allowed to view their transactions.
    Transactions are created with Stripe payment intents.
    Transactions are only updated to confirm pending payment intents.
    A use should not be able to delete a transaction.
    """

    permission_classes = (permissions.IsAuthenticated,)
    serializer_classes = {
        "read": PaymentTransactionReadOnlySerializer,
        "create": PaymentTransactionCreateSerializer,
        "update": PaymentTransactionUpdateSerializer,
    }

    def get_queryset(self):
        user = self.request.user
        return PaymentTransaction.objects.filter(user=user)

    def destroy(self, request, *args, **kwargs):
        return Response(
            {"message": "Du kan ikke slette eksisterende transaksjoner"},
            status.HTTP_403_FORBIDDEN,
        )
