# -*- coding: utf-8 -*-

import json
import stripe

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.utils.translation import ugettext as _ 

from apps.payment.models import Payment, PaymentRelation
from apps.events.models import Event


def payment(request, event_id, payment_id):
	stripe.api_key = "sk_test_BQokikJOvBiI2HlWgH4olfQ2"

	print "Event id: " + event_id

	# Get the credit card details submitted by the form
	token = request.POST["stripeToken"]

	event = Events.objects.get(id=event_id)
	payment = Payment.objects.get(id=payment_id, content_type=ContentType.objects.get_for_model(Event), object_id=event_id)

	# Create the charge on Stripe's servers - this will charge the user's card
	try:
	  charge = stripe.Charge.create(
	      amount=payment.price, # amount in cents, again
	      currency="nok",
	      card=token,
	      description=request.user.email
	  )
	  messages.success(request, _(u"Betaling utført."))
	except stripe.CardError, e:
	  messages.error(request, _(u"Betaling feilet."))
	  pass

	return HttpResponseRedirect('/')

def payment_info(request):
	if 'payment_id' in request.session and 'event_id' in request.session:

		data = dict()

		payment = get_object_or_404(Payment, pk=request.session['payment_id'])
		event = get_object_or_404(Event, pk=request.session['event_id'])

		data['price'] = payment.price
		data['stripe_price'] = payment.price * 100
		data['payment_id'] = payment.id
		data['event_id'] = event.id
		data['email'] = request.user.email

		data['description'] = event.title

		return HttpResponse(json.dumps(data), content_type="application/json")
