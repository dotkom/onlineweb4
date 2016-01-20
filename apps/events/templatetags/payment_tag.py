from django import template

register = template.Library()


@register.inclusion_tag('events/payment_tag.html')
def display_payments(payment, payment_delay):
    return {'payment': payment, 'payment_delay': payment_delay}