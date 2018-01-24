# -*- coding: utf-8 -*-

import json
import logging

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage, send_mail
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from pytz import timezone as tz

from apps.payment.models import Payment, PaymentPrice, PaymentRelation, PaymentTransaction, ReceiptItem, PaymentReceipt
from apps.webshop.models import OrderLine


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

                    payment_relation = PaymentRelation.objects.create(
                        payment=payment_object,
                        payment_price=payment_price,
                        user=request.user,
                        stripe_id=charge.id
                    )

                    payment_object.handle_payment(request.user)

                    _send_payment_confirmation_mail(payment_relation)

                    messages.success(request, _("Betaling utført."))
                    return HttpResponse("Betaling utført.", content_type="text/plain", status=200)
                except stripe.CardError as e:
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

                receipt = PaymentReceipt(
                    to_mail=request.user.email,
                    from_mail=settings.EMAIL_PROKOM,
                    subject="[kvittering] webshop",
                    description="varer i webshop",
                    transaction_date=order_line.datetime
                )
                receipt.save()

                for order in order_line.orders.all():
                    item = ReceiptItem(
                        receipt=receipt,
                        name=order.product.name,
                        price=int(order.price/order.quantity),
                        quantity=order.quantity
                    )
                    item.save()

                _send_receipt(receipt)

                messages.success(request, "Betaling utført")

                return HttpResponse("Betaling utført.", content_type="text/plain", status=200)
            except stripe.CardError as e:
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

        payment_relation.payment.handle_refund(request.META['HTTP_HOST'], payment_relation)
        messages.success(request, _("Betalingen har blitt refundert."))
    except stripe.InvalidRequestError as e:
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

                payment_transaction = PaymentTransaction.objects.create(user=request.user, amount=amount,
                                                                        used_stripe=True)

                receipt = PaymentReceipt(
                    to_mail=payment_transaction.user.email,
                    from_mail=settings.EMAIL_TRIKOM,
                    subject="[kvittering] saldo inskudd",
                    description="påfyll av saldo",
                    transaction_date=payment_transaction.datetime,
                )
                receipt.save()

                item = ReceiptItem(
                    receipt=receipt,
                    name='Saldo',
                    price=int(payment_transaction.amount)
                )

                item.save()

                _send_receipt(receipt)

                messages.success(request, _("Inskudd utført."))
                return HttpResponse("Inskudd utført.", content_type="text/plain", status=200)
            except stripe.CardError as e:
                messages.error(request, str(e))
                return HttpResponse(str(e), content_type="text/plain", status=500)

    raise Http404("Request not supported")


# Confirmation Mails
def _send_payment_confirmation_mail(payment_relation):
    subject = _("kvittering") + ": " + payment_relation.payment.description()
    from_mail = payment_relation.payment.responsible_mail()
    to_mails = [payment_relation.user.email]

    items = [
        {
            'amount': int(payment_relation.payment_price.price),
            'description': payment_relation.payment.description
        },
    ]

    context = {
        'payment_date': payment_relation.datetime.astimezone(tz('Europe/Oslo')).strftime("%-d %B %Y kl. %H:%M"),
        'description': payment_relation.payment.description,
        'payment_id': payment_relation.unique_id,
        'items': items,
        'total_amount': sum(item['amount'] for item in items),
        'to_mail': to_mails,
        'from_mail': from_mail
    }

    email_message = render_to_string('payment/email/confirmation_mail.txt', context)
    send_mail(subject, email_message, from_mail, to_mails)


def _send_receipt(receipt):
    subject = receipt.subject
    from_mail = receipt.from_mail
    to_mails = [receipt.to_mail]

    items = []
    total_amount = 0
    for item in receipt.items.all():
        items.append({
            'amount': item.price,
            'description': item.name,
            'quantity': item.quantity
        })
        total_amount += item.price * item.quantity
    print('items:', items)

    context = {
        'payment_date': receipt.transaction_date,
        'description': receipt.description,
        'payment_id': receipt.receipt_id,
        'items': items,
        'total_amount': total_amount,
        'to_mail': to_mails,
        'from_mail': from_mail
    }

    email_message = render_to_string('payment/email/confirmation_mail.txt', context)
    send_mail(subject, email_message, from_mail, to_mails)
