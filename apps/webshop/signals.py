import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.payment.models import Payment, PaymentPrice
from apps.webshop.models import Order, OrderLine

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Order)
def sync_order_line_subtotal_to_payment_price(sender, instance: Order, **kwargs):
    """
    Keep the price and status of the Payment with the OrderLine
    """
    order_line: OrderLine = instance.order_line
    payment: Payment = order_line.payment
    if payment:
        payment_price: PaymentPrice = payment.price()
        """
        Webshop Order Lines should only have a single payment with a single Price.
        If it exists it should be updated. If it does not it has to be created.
        """
        if not payment_price:
            PaymentPrice.objects.create(
                payment=payment,
                price=order_line.subtotal(),
                description=order_line.payment_description,
            )
        else:
            payment_price.price = order_line.subtotal()
            payment_price.description = order_line.payment_description
            payment_price.save()


@receiver(post_save, sender=OrderLine)
def create_payment_for_order_line(
    sender, instance: OrderLine, created: bool = False, **kwargs
):
    """
    Order Lines should have a payment connected to them when they are created.
    There should only be a single payment connected to each Webshop Order Line, with a single price.
    """
    if not instance.payment and created:
        """ Webshop Payments are always made to Prokom, and always require immediate payment """
        Payment.objects.create(
            stripe_key="prokom", payment_type=1, content_object=instance, active=True
        )
