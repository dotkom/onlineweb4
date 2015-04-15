from django import template

register = template.Library()

@register.filter
def contains_instant_payment(payments):
	for payment in payments:
		if payment.payment_type == 1:
			return True

	return False


@register.inclusion_tag('events/payment_tag.html')
def display_payments(payments, payment_delay):
    return {'payments': payments, 'payment_delay': payment_delay}