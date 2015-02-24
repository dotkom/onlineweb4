# -*- coding: utf-8 -*-

import json
import stripe

from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
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
                content_type = ContentType.objects.get_for_id(payment.content_type.id)
                content_object = content_type.get_object_for_this_type(pk=payment.object_id)

                try:
                    charge = stripe.Charge.create(
                      amount=payment.price * 100, #Price is multiplied with 100 because the amount is in øre
                      currency="nok",
                      card=token,
                      description=payment_description(content_object) + " - " + request.user.email
                    )

                    PaymentRelation.objects.create(payment=payment, user=request.user)

                    handle_post_payment(content_object, request.user)

                    #TODO send mail

                    messages.success(request, _(u"Betaling utført."))
                    return HttpResponse("Betaling utført.", content_type="text/plain", status=200) 
                except stripe.CardError, e:
                    messages.error(request, _(u"Betaling feilet: ") + str(e))
                    return HttpResponse(str(e), content_type="text/plain", status=500) 

        #TODO return error messages

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
            data['description'] = payment_description(content_object)


            data['payment_ids'] = request.session['payment_ids']

            for payment in payments:
                data[payment.id] = dict()
                data[payment.id]['price'] = payment.price
                #The price is in øre so it needs to be multiplied with 100
                data[payment.id]['stripe_price'] = payment.price * 100
                data[payment.id]['payment_id'] = payment.id

            return HttpResponse(json.dumps(data), content_type="application/json")

    return HttpResponse("Failed to get info", content_type="text/plain", status=500) 


def payment_description(content_object):
    if hasattr(content_object, "payment_description"):
        return content_object.payment_description()

    return "payment description not implemented"

def handle_post_payment(content_object, user):
    if hasattr(content_object, "payment_complete"):
        content_object.payment_complete(user)
