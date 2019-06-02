# -*- coding: utf-8 -*-

import json
import logging

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from stripe.error import CardError, InvalidRequestError, StripeError

from apps.payment import status as payment_status
from apps.payment.models import (Payment, PaymentDelay, PaymentPrice, PaymentRelation,
                                 PaymentTransaction)
from apps.payment.serializers import (PaymentDelayReadOnlySerializer,
                                      PaymentPriceReadOnlySerializer,
                                      PaymentRelationCreateSerializer,
                                      PaymentRelationReadOnlySerializer,
                                      PaymentRelationUpdateSerializer,
                                      PaymentTransactionCreateSerializer,
                                      PaymentTransactionReadOnlySerializer,
                                      PaymentTransactionUpdateSerializer)
from apps.webshop.models import OrderLine

logger = logging.getLogger(__name__)


@login_required
def payment(request):
    if request.is_ajax():
        if request.method == "POST":

            # Get the credit card details submitted by the form
            token = request.POST.get("stripeToken")
            payment_id = request.POST.get("paymentId")
            price_id = request.POST.get("priceId")

            payment_object = Payment.objects.get(id=payment_id)
            payment_price = PaymentPrice.objects.get(id=price_id)

            if payment_object:
                try:
                    stripe.api_key = settings.STRIPE_PRIVATE_KEYS[payment_object.stripe_key]

                    charge = stripe.Charge.create(
                        amount=payment_price.price * 100,  # Price is multiplied with 100 because the amount is in øre
                        currency="nok",
                        card=token,
                        description=payment_object.description() + " - " + request.user.email
                    )

                    PaymentRelation.objects.create(
                        payment=payment_object,
                        payment_price=payment_price,
                        user=request.user,
                        stripe_id=charge.id
                    )

                    payment_object.handle_payment(request.user)

                    messages.success(request, _("Betaling utført."))
                    return HttpResponse("Betaling utført.", content_type="text/plain", status=200)
                except CardError as e:
                    messages.error(request, str(e))
                    return HttpResponse(str(e), content_type="text/plain", status=500)

    raise Http404("Request not supported")


@login_required
def payment_info(request):
    if request.is_ajax():
        if 'payment_id' in request.session:

            data = dict()

            payment_object = Payment.objects.get(id=request.session['payment_id'])

            if payment_object:
                data['stripe_public_key'] = settings.STRIPE_PUBLIC_KEYS[payment_object.stripe_key]
                data['email'] = request.user.email
                data['description'] = payment_object.description()
                data['payment_id'] = request.session['payment_id']
                data['price_ids'] = [price.id for price in payment_object.prices()]

                for payment_price in payment_object.prices():
                    data[payment_price.id] = dict()
                    data[payment_price.id]['price'] = payment_price.price
                    # The price is in øre so it needs to be multiplied with 100
                    data[payment_price.id]['stripe_price'] = payment_price.price * 100

                return HttpResponse(json.dumps(data), content_type="application/json")

    raise Http404("Request not supported")


@login_required
def webshop_info(request):
    if request.is_ajax():
        data = dict()

        # TODO fix get order_line
        order_line = OrderLine.objects.filter(user=request.user, paid=False).first()

        if order_line:
            data['stripe_public_key'] = settings.STRIPE_PUBLIC_KEYS["prokom"]
            data['email'] = request.user.email
            data['order_line_id'] = order_line.pk
            data['price'] = int(order_line.subtotal() * 100)

            return HttpResponse(json.dumps(data), content_type="application/json")

    raise Http404("Request not supported")


@login_required
def webshop_pay(request):
    if request.is_ajax():
        if request.method == "POST":

            # Get the credit card details submitted by the form
            token = request.POST.get("stripeToken")
            amount = int(request.POST.get("amount"))
            order_line_id = request.POST.get("order_line_id")

            order_line = OrderLine.objects.get(pk=order_line_id)

            # Check if the user has added or removed items since reloading the checkout page
            if int(order_line.subtotal() * 100) != amount:
                messages.error(request, "Det har skjedd endringer på bestillingen. Prøv igjen")
                return HttpResponse("Invalid input", content_type="text/plain", status=500)

            try:
                stripe.api_key = settings.STRIPE_PRIVATE_KEYS["prokom"]

                if not order_line.is_valid():
                    error = "Ordren er ikke gyldig."
                    messages.error(request, error)
                    return HttpResponse(error, content_type="text/plain", status=400)

                charge = stripe.Charge.create(
                    amount=amount,
                    currency="nok",
                    card=token,
                    description="Web shop purchase - " + request.user.email
                )

                order_line.pay()
                order_line.stripe_id = charge.id
                order_line.save()

                messages.success(request, "Betaling utført")

                return HttpResponse("Betaling utført.", content_type="text/plain", status=200)
            except CardError as e:
                messages.error(request, str(e))
                return HttpResponse(str(e), content_type="text/plain", status=500)

    raise Http404("Request not supported")


@login_required
def payment_refund(request, payment_relation_id):
    payment_relation = get_object_or_404(PaymentRelation, pk=payment_relation_id)

    # Prevents users from refunding others
    if request.user != payment_relation.user:
        return HttpResponse("Unauthorized user", content_type="text/plain", status=403)

    status = payment_relation.payment.check_refund(payment_relation)

    if not status[0]:
        messages.error(request, status[1])
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    try:
        stripe.api_key = settings.STRIPE_PRIVATE_KEYS[payment_relation.payment.stripe_key]
        ch = stripe.Charge.retrieve(payment_relation.stripe_id)
        ch.refunds.create()

        payment_relation.payment.handle_refund(payment_relation)
        messages.success(request, _("Betalingen har blitt refundert."))
    except InvalidRequestError as e:
        messages.error(request, str(e))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def saldo_info(request):
    if request.is_ajax():
        data = dict()

        data['stripe_public_key'] = settings.STRIPE_PUBLIC_KEYS["trikom"]
        data['email'] = request.user.email
        return HttpResponse(json.dumps(data), content_type="application/json")

    raise Http404("Request not supported")


@login_required
def saldo(request):
    if request.is_ajax():
        if request.method == "POST":

            # Get the credit card details submitted by the form
            token = request.POST.get("stripeToken")
            amount = int(request.POST.get("amount"))

            if amount not in (100, 200, 500):
                messages.error(request, "Invalid input")
                return HttpResponse("Invalid input", content_type="text/plain", status=500)

            try:
                stripe.api_key = settings.STRIPE_PRIVATE_KEYS["trikom"]

                stripe.Charge.create(
                    amount=amount * 100,  # Price is multiplied with 100 because the amount is in øre
                    currency="nok",
                    card=token,
                    description="Saldo deposit - " + request.user.email
                )

                PaymentTransaction.objects.create(user=request.user, amount=amount, used_stripe=True)

                messages.success(request, _("Inskudd utført."))
                return HttpResponse("Inskudd utført.", content_type="text/plain", status=200)
            except CardError as e:
                messages.error(request, str(e))
                return HttpResponse(str(e), content_type="text/plain", status=500)

    raise Http404("Request not supported")


class PaymentDelayReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Allow users to view their own payment delays.
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PaymentDelayReadOnlySerializer

    def get_queryset(self):
        user = self.request.user
        return PaymentDelay.objects.filter(user=user)


class PaymentRelationViewSet(viewsets.ModelViewSet):

    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        """
        Get different serializers for creating (paying) and listing/retrieving previous payments.
        Delete does not use a serializer, and logic resides in the view.
        """
        if self.action in ['list', 'retrieve']:
            return PaymentRelationReadOnlySerializer
        if self.action == 'create':
            return PaymentRelationCreateSerializer
        if self.action in ['update', 'partial_update']:
            return PaymentRelationUpdateSerializer

        return super().get_serializer_class()

    def get_queryset(self):
        user = self.request.user
        return PaymentRelation.objects.filter(user=user)

    def destroy(self, request, *args, **kwargs):
        """
        Destroy logic is set in the view because serializers cannot delete.
        """
        user = request.user
        payment_relation: PaymentRelation = self.get_object()
        can_refund, message = payment_relation.payment.check_refund(payment_relation)

        if not can_refund:
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)

        try:
            """ Handle the actual refund with the stripe API """
            stripe.api_key = payment_relation.payment.stripe_private_key
            intent = stripe.PaymentIntent.retrieve(payment_relation.stripe_id)

            if payment_relation.status in [payment_status.SUCCEEDED, payment_status.DONE]:
                intent['charges']['data'][0].refund()

            elif payment_relation.status == payment_status.PENDING:
                intent.cancel()

            elif payment_relation.status in [payment_status.REFUNDED, payment_status.REMOVED]:
                return Response({
                    'message': _("Denne betalingen har allerede blitt refundert.")
                }, status.HTTP_400_BAD_REQUEST)

            return Response({'message': _("Betalingen har blitt refundert.")}, status.HTTP_200_OK)

        except (InvalidRequestError, StripeError, Exception) as error:
            logger.error(f'An error occurred during refund of payment: {payment_relation} '
                         f'to stripe for user: {user}', error)
            return Response({
                'message': 'Det skjedde en feil under behandlingen av refunderingen'
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentPriceReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PaymentPriceReadOnlySerializer
    queryset = PaymentPrice.objects.all()


class PaymentTransactionViewSet(viewsets.ModelViewSet):
    """
    A user should be allowed to view their transactions.
    Transactions are created with Stripe payment intents.
    Transactions are only updated to confirm pending payment intents.
    A use should not be able to delete a transaction.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return PaymentTransactionReadOnlySerializer
        if self.action == 'create':
            return PaymentTransactionCreateSerializer
        if self.action in ['update', 'partial_update']:
            return PaymentTransactionUpdateSerializer

        super().get_serializer_class()

    def get_queryset(self):
        user = self.request.user
        return PaymentTransaction.objects.filter(user=user)

    def destroy(self, request, *args, **kwargs):
        return Response({'message': 'Du kan ikke slette eksisterende transaksjoner'}, status.HTTP_403_FORBIDDEN)
