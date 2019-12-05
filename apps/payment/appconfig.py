from django.apps import AppConfig


class PaymentConfig(AppConfig):
    name = "apps.payment"
    verbose_name = "Payment"

    def ready(self):
        super().ready()
        # The following stops pycharm from nagging about unused import statement
        # noinspection PyUnresolvedReferences
        import apps.payment.signals  # noqa: F401
