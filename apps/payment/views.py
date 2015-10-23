# -*- coding: utf-8 -*-

import json
import stripe

from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext as _ 

from apps.payment.models import Payment, PaymentRelation, PaymentPrice, PaymentTransaction

@login_required
def payment(request):

    if request.is_ajax():
        if request.method == "POST":

            # Get the credit card details submitted by the form
            token = request.POST.get("stripeToken")
            payment_id = request.POST.get("paymentId")
            price_id = request.POST.get("priceId")

            payment = Payment.objects.get(id=payment_id)
            payment_price = PaymentPrice.objects.get(id=price_id) 

            if payment:
                try:
                    stripe.api_key = settings.STRIPE_PRIVATE_KEYS[payment.stripe_key_index]

                    charge = stripe.Charge.create(
                      amount=payment_price.price * 100, #Price is multiplied with 100 because the amount is in øre
                      currency="nok",
                      card=token,
                      description=payment.description() + " - " + request.user.email
                    )

                    payment_relation = PaymentRelation.objects.create(payment=payment, 
                        payment_price=payment_price, user=request.user, stripe_id=charge.id)

                    payment.handle_payment(request.user)

                    _send_payment_confirmation_mail(payment_relation)

                    messages.success(request, _(u"Betaling utført."))
                    return HttpResponse("Betaling utført.", content_type="text/plain", status=200) 
                except stripe.CardError, e:
                    messages.error(request, str(e))
                    return HttpResponse(str(e), content_type="text/plain", status=500) 


    raise Http404("Request not supported");


@login_required
def payment_info(request):

    if request.is_ajax():
        if 'payment_id' in request.session:

            data = dict()

            payment = Payment.objects.get(id=request.session['payment_id'])

            if payment:
                data['stripe_public_key'] = settings.STRIPE_PUBLIC_KEYS[payment.stripe_key_index]
                data['email'] = request.user.email
                data['description'] = payment.description()
                data['payment_id'] = request.session['payment_id']
                data['price_ids'] = [price.id for price in payment.prices()]

                for payment_price in payment.prices():
                    data[payment_price.id] = dict()
                    data[payment_price.id]['price'] = payment_price.price
                    #The price is in øre so it needs to be multiplied with 100
                    data[payment_price.id]['stripe_price'] = payment_price.price * 100

                return HttpResponse(json.dumps(data), content_type="application/json")

    raise Http404("Request not supported");

@login_required
def payment_refund(request, payment_relation_id):

    payment_relation = get_object_or_404(PaymentRelation, pk=payment_relation_id)

    #Prevents users from refunding others
    if request.user != payment_relation.user:
        return HttpResponse("Unauthorized user", content_type="text/plain", status=403)

    status = payment_relation.payment.check_refund(payment_relation)

    if not status[0]:
        messages.error(request, status[1])
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    try:
        stripe.api_key = settings.STRIPE_PRIVATE_KEYS[payment_relation.payment.stripe_key_index]
        ch = stripe.Charge.retrieve(payment_relation.stripe_id)
        re = ch.refunds.create()

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

    email = EmailMessage(subject, unicode(message), from_mail, [], to_mails).send()


@login_required
def saldo_info(request):

    if request.is_ajax():

        data = dict()

        data['stripe_public_key'] = settings.STRIPE_PUBLIC_KEYS[1] #TODO fix right key 
        data['email'] = request.user.email
        return HttpResponse(json.dumps(data), content_type="application/json")

    raise Http404("Request not supported");


@login_required
def saldo(request):

    if request.is_ajax():
        if request.method == "POST":

            # Get the credit card details submitted by the form
            token = request.POST.get("stripeToken")
            amount = int(request.POST.get("amount"))

            if not amount in (100, 200, 500):
                messages.error(request, "Invalid input")
                return HttpResponse("Invalid input", content_type="text/plain", status=500) 

            try:
                stripe.api_key = settings.STRIPE_PRIVATE_KEYS[1] #TODO fix index

                charge = stripe.Charge.create(
                  amount=amount * 100, #Price is multiplied with 100 because the amount is in øre
                  currency="nok",
                  card=token,
                  description="Saldo deposit - " + request.user.email
                )

                PaymentTransaction.objects.create(user=request.user, amount=amount, used_stripe=True)

                request.user.saldo += amount
                request.user.save()
                _send_saldo_confirmation_mail(request.user.email, amount)

                messages.success(request, _(u"Inskudd utført."))
                return HttpResponse("Inskudd utført.", content_type="text/plain", status=200) 
            except stripe.CardError, e:
                messages.error(request, str(e))
                return HttpResponse(str(e), content_type="text/plain", status=500) 


    raise Http404("Request not supported");

def _send_saldo_confirmation_mail(email, amount):
    subject = _(u"kvittering saldo inskudd")
    from_mail = settings.EMAIL_TRIKOM

    message = _(u"Kvitering på saldo inskudd på ") + amount 
    message += _(u" til din Online saldo.")
    message += "\n"
    message += "\n"
    message += _(u"Dersom du har problemer eller spørsmål, send mail til") + ": " + from_mail

    email = EmailMessage(subject, unicode(message), from_mail, [], [email]).send()
