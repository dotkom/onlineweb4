from django.apps import AppConfig


class PaymentConfig(AppConfig):
    name = "apps.payment"
    verbose_name = "Payment"

    def ready(self):
        super(PaymentConfig, self).ready()

        import apps.payment.signals  # noqa: F401
