from django.shortcuts import render


def pay(request):
	stripe.api_key = "sk_test_BQokikJOvBiI2HlWgH4olfQ2"

	# Get the credit card details submitted by the form
	token = request.POST['stripeToken']
	#TODO get paymentid from POST

	# Create the charge on Stripe's servers - this will charge the user's card
	try:
	  charge = stripe.Charge.create(
	      amount=1000, # amount in cents, again
	      currency="nok",
	      card=token,
	      description="payinguser@example.com"
	  )
	except stripe.CardError, e:
	  # The card has been declined
	  pass

	# Create your views here.
