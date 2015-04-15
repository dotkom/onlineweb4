# -*- coding: utf-8 -*-

import json
import stripe

from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.utils.translation import ugettext as _ 

from apps.payment.models import Payment, PaymentRelation
from apps.events.models import Event, Attendee

@login_required
def payment(request):

    if request.is_ajax():
        if request.method == "POST":
            stripe.api_key = settings.STRIPE_PRIVATE_KEY

            # Get the credit card details submitted by the form
            token = request.POST.get("stripeToken")
            payment_id = request.POST.get("paymentId")

            payment = Payment.objects.get(id=payment_id)

            if payment:
                try:
                    charge = stripe.Charge.create(
                      amount=payment.price * 100, #Price is multiplied with 100 because the amount is in øre
                      currency="nok",
                      card=token,
                      description=payment.description() + " - " + request.user.email
                    )

                    payment_relation = PaymentRelation.objects.create(payment=payment, user=request.user)

                    payment.handle_payment(request.user)

                    send_payment_confirmation_mail(payment_relation)

                    messages.success(request, _(u"Betaling utført."))
                    return HttpResponse("Betaling utført.", content_type="text/plain", status=200) 
                except stripe.CardError, e:
                    messages.error(request, str(e))
                    return HttpResponse(str(e), content_type="text/plain", status=500) 


    raise Http404("Request not supported");


@login_required
def payment_info(request):
    if 'payment_ids' in request.session:

        data = dict()

        payments = Payment.objects.filter(id__in=request.session['payment_ids'])

        if payments:
            content_type = ContentType.objects.get_for_id(payments[0].content_type.id)
            content_object = content_type.get_object_for_this_type(pk=payments[0].object_id)

            data['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
            data['email'] = request.user.email
            data['description'] = payments[0].description()
            data['payment_ids'] = request.session['payment_ids']

            for payment in payments:
                data[payment.id] = dict()
                data[payment.id]['price'] = payment.price
                #The price is in øre so it needs to be multiplied with 100
                data[payment.id]['stripe_price'] = payment.price * 100
                data[payment.id]['payment_id'] = payment.id

            return HttpResponse(json.dumps(data), content_type="application/json")

    return HttpResponse("Failed to get info", content_type="text/plain", status=500) 

def send_payment_confirmation_mail(payment_relation):
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
