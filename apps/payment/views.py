# -*- coding: utf-8 -*-

import json
import stripe

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from apps.payment.models import Payment, PaymentRelation, PaymentPrice
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
                    stripe.api_key = settings.STRIPE_PRIVATE_KEYS[payment_object.stripe_key_index]

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

                    messages.success(request, _(u"Betaling utført."))
                    return HttpResponse("Betaling utført.", content_type="text/plain", status=200)
                except stripe.CardError, e:
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
                data['stripe_public_key'] = settings.STRIPE_PUBLIC_KEYS[payment_object.stripe_key_index]
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

        #TODO fix get order_line
        order_line = OrderLine.objects.filter(user=request.user, paid=False).first()

        if order_line:
            data['stripe_public_key'] = settings.STRIPE_PUBLIC_KEYS[1] #Prokom
            data['email'] = request.user.email
            data['order_line_id'] = order_line.pk
            data['price'] = int(order_line.subtotal() * 100)

            return HttpResponse(json.dumps(data), content_type="application/json")

    raise Http404("Request not supported");


@login_required
def webshop_pay(request):

    if request.is_ajax():
        if request.method == "POST":

            # Get the credit card details submitted by the form
            token = request.POST.get("stripeToken")
            amount = int(request.POST.get("amount"))
            order_line_id = request.POST.get("order_line_id")

            order_line = OrderLine.objects.get(pk=order_line_id)

            #Check if the user has added or removed items since reloading the checkout page
            if int(order_line.subtotal() * 100) != amount:
                messages.error(request, u"Det har skjedd endringer på bestillingen. Prøv igjen")
                return HttpResponse("Invalid input", content_type="text/plain", status=500) 

            try:
                stripe.api_key = settings.STRIPE_PRIVATE_KEYS[1] #Prokom

                charge = stripe.Charge.create(
                  amount=amount,
                  currency="nok",
                  card=token,
                  description="Web shop purchase - " + request.user.email
                )

                order_line.pay()

                messages.success(request, "Betaling utført")

                return HttpResponse("Betaling utført.", content_type="text/plain", status=200) 
            except stripe.CardError, e:
                messages.error(request, str(e))
                return HttpResponse(str(e), content_type="text/plain", status=500) 


    raise Http404("Request not supported");

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
        stripe.api_key = settings.STRIPE_PRIVATE_KEYS[payment_relation.payment.stripe_key_index]
        ch = stripe.Charge.retrieve(payment_relation.stripe_id)
        ch.refunds.create()

        payment_relation.payment.handle_refund(request.META['HTTP_HOST'], payment_relation)
        messages.success(request, _("Betalingen har blitt refundert."))
    except stripe.InvalidRequestError, e:
        messages.error(request, str(e))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def _send_payment_confirmation_mail(payment_relation):
    subject = _(u"kvittering") + ": " + payment_relation.payment.description()
    from_mail = payment_relation.payment.responsible_mail()
    to_mails = [payment_relation.user.email]

    message = _(u"Du har betalt for ") + payment_relation.payment.description()
    message += "\n"
    message += _(u"Ditt kvitteringsnummer er") + ": " + payment_relation.unique_id
    message += "\n"
    message += "\n"
    message += _(u"Dersom du har problemer eller spørsmål, send mail til") + ": " + from_mail

    EmailMessage(subject, unicode(message), from_mail, [], to_mails).send()
