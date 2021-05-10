from abc import abstractmethod
from typing import List

from django.conf import settings
from django.utils import timezone

from apps.authentication.models import OnlineUser as User


class PaymentMixin:
    """
    Mixin for models related to the a payment.
    Each abstract method should be overridden to handle payment correctly from that model type.

    To allow payments for new model, just subclass this mixin in the model and implement all methods.
    """

    @abstractmethod
    def get_payment_description(self) -> str:
        return "No description (unsupported content type)"

    @abstractmethod
    def get_payment_email(self) -> str:
        """
        :return the email of the responsible committee/group/user which created or handles the payment.
        """
        return settings.DEFAULT_FROM_EMAIL

    @abstractmethod
    def is_user_allowed_to_pay(self, user: User) -> bool:
        """There are no rules prohibiting user from paying for other types of payments"""
        return True

    @abstractmethod
    def can_refund_payment(self, payment_relation) -> (bool, str):
        return (
            False,
            "Denne betalingen er koblet til en ikke-støttet objekttype, og kan derfor ikke refunderes",
        )

    @abstractmethod
    def on_payment_done(self, user: User):
        """
        Handle the effect of a payment being done/completed for a user.
        """
        pass

    @abstractmethod
    def on_payment_refunded(self, payment_relation):
        """
        Handle the effects of payment relation being refunded.
        """
        pass

    @abstractmethod
    def get_payment_receipt_items(self, payment_relation) -> List[dict]:
        return []


class ReceiptMixin:
    @abstractmethod
    def get_receipt_timestamp(self) -> timezone.datetime:
        pass

    @abstractmethod
    def get_receipt_subject(self) -> str:
        pass

    @abstractmethod
    def get_receipt_description(self) -> str:
        pass

    @abstractmethod
    def get_receipt_items(self) -> List[dict]:
        pass

    @abstractmethod
    def get_receipt_from_email(self) -> str:
        pass

    @abstractmethod
    def get_receipt_to_user(self) -> User:
        pass
