from django.shortcuts import render

from apps.payment.models import Payment, PaymentRelation
from apps.events.models import Event


def payment(request, event_id, payment_id):
	stripe.api_key = "sk_test_BQokikJOvBiI2HlWgH4olfQ2"

	# Get the credit card details submitted by the form
	token = request.POST['stripeToken']

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
	except stripe.CardError, e:
	  # The card has been declined
	  pass

	# Create your views here.
