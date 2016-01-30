from django.apps import AppConfig


class PaymentConfig(AppConfig):
    name = 'apps.payment'
    verbose_name = 'Payment'

    def ready(self):
        super(PaymentConfig, self).ready()

        from reversion import revisions as reversion

        from apps.payment.models import PaymentTransaction

        reversion.register(PaymentTransaction)
