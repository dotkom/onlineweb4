from django import template
import re

register = template.Library()

@register.filter
def contains_instant_payment(payments):
	for payment in payments:
		if payment.instant_payment:
			return True

	return False


@register.inclusion_tag('events/payment_tag.html')
def display_payments(payments):
    return {'payments': payments}