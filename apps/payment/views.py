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
            event_id = request.POST.get("eventId")
            payment_id = request.POST.get("paymentId")

            event = Event.objects.get(id=event_id)
            payment = Payment.objects.get(id=payment_id, content_type=ContentType.objects.get_for_model(Event), object_id=event_id)

            try:
                charge = stripe.Charge.create(
                  amount=payment.price * 100, #Price is multiplied with 100 because the amount is in øre
                  currency="nok",
                  card=token,
                  description=request.user.email
                )

                PaymentRelation.objects.create(payment=payment, user=request.user)
                Attendee.objects.create(event=event.attendance_event, user=request.user)

                #TODO send mail

                messages.success(request, _(u"Betaling utført."))
                return HttpResponse("Betaling utført.", content_type="text/plain", status=200) 
            except stripe.CardError, e:
                messages.error(request, _(u"Betaling feilet: ") + str(e))
                return HttpResponse(str(e), content_type="text/plain", status=500) 

@login_required
def payment_info(request):
    if 'payment_ids' in request.session and 'event_id' in request.session:

        data = dict()

        event = get_object_or_404(Event, pk=request.session['event_id'])

        data['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        data['event_id'] = event.id
        data['email'] = request.user.email
        data['description'] = event.title

        payments = Payment.objects.filter(id__in=request.session['payment_ids'])

        data['payment_ids'] = request.session['payment_ids']

        for payment in payments:
            data[payment.id] = dict()
            data[payment.id]['price'] = payment.price
            #The price is in øre so it needs to be multiplied with 100
            data[payment.id]['stripe_price'] = payment.price * 100
            data[payment.id]['payment_id'] = payment.id

        return HttpResponse(json.dumps(data), content_type="application/json")
