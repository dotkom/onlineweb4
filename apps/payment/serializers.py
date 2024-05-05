import logging

import stripe
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from apps.payment import status
from apps.payment.models import Payment, PaymentDelay, PaymentPrice, PaymentRelation

logger = logging.getLogger(__name__)


class PaymentPriceReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentPrice
        fields = ("id", "price", "description")
        read_only = True


class PaymentReadOnlySerializer(serializers.ModelSerializer):
    payment_prices = PaymentPriceReadOnlySerializer(
        many=True, source="paymentprice_set"
    )
    payment_type_display = serializers.CharField(source="get_payment_type_display")
    content_type = serializers.SerializerMethodField()

    def get_content_type(self, obj: Payment):
        return f"{obj.content_type.app_label}.{obj.content_type.model}"

    class Meta:
        model = Payment
        fields = (
            "id",
            "object_id",
            "content_type",
            "payment_type",
            "payment_type_display",
            "payment_prices",
            "description",
            "stripe_public_key",
        )
        read_only = True


class PaymentRelationReadOnlySerializer(serializers.ModelSerializer):
    payment = PaymentReadOnlySerializer(read_only=True)
    payment_price = PaymentPriceReadOnlySerializer(read_only=True)

    class Meta:
        model = PaymentRelation
        fields = (
            "id",
            "payment",
            "payment_price",
            "datetime",
            "refunded",
            "payment_intent_secret",
            "status",
            "is_refundable",
            "is_refundable_reason",
        )
        read_only = True


class PaymentDelayReadOnlySerializer(serializers.ModelSerializer):
    payment = PaymentReadOnlySerializer()

    class Meta:
        model = PaymentDelay
        fields = ("payment", "valid_to", "active")
        read_only = True


class PaymentRelationCreateSerializer(serializers.ModelSerializer):
    """
    Relates the user, to a payment, stripe intent and price
    """

    payment = serializers.PrimaryKeyRelatedField(
        required=True, queryset=Payment.objects.all()
    )
    payment_price = serializers.PrimaryKeyRelatedField(
        required=True, queryset=PaymentPrice.objects.all()
    )
    payment_method_id = serializers.CharField(write_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate(self, data):
        payment = data.get("payment")
        payment_price = data.get("payment_price")
        valid_price_pks = [
            price.pk for price in PaymentPrice.objects.filter(payment=payment)
        ]

        if payment_price.id not in valid_price_pks:
            raise serializers.ValidationError(
                "Supplied payment price is not valid for the supplied payment"
            )

        return data

    def create(self, validated_data):
        """
        Overwrite create to handle the stripe charge before the relation is created.
        """
        request = self.context.get("request")
        user = request.user

        payment: Payment = validated_data.get("payment")
        payment_price: PaymentPrice = validated_data.get("payment_price")

        if not payment.is_user_allowed_to_pay(user):
            raise serializers.ValidationError(
                "Du har ikke tilgang til å betale for denne betalingen"
            )

        """ Get stripe token and remove it from the data that from the create data """
        payment_method_id = validated_data.pop("payment_method_id")

        payment_relation: PaymentRelation = super().create(
            {**validated_data, "status": status.PENDING}
        )

        logger.info(
            f"Set up Stripe for payment:{payment.id}, user:{request.user.id}, "
            f"price: {payment_price.price} kr"
        )
        try:
            """Validate and make the Intent with the Stripe payment method"""
            intent = stripe.PaymentIntent.create(
                payment_method=payment_method_id,
                amount=payment_price.price
                * 100,  # Price is multiplied with 100 because the amount is in øre
                currency="nok",
                confirmation_method="manual",
                confirm=True,
                description=f"{payment.description()} - {request.user.email}",
                api_key=payment.stripe_private_key,
            )

            # If the payment needs more validation by Stripe or the bank
            if (
                intent.status == "requires_source_action"
                and intent.next_action.type == "use_stripe_sdk"
            ):
                payment_relation.status = status.PENDING
                payment_relation.payment_intent_secret = intent.client_secret

            elif intent.status == "succeeded":
                payment_relation.status = status.SUCCEEDED

            else:
                logger.error(
                    f"Payment intent returned an invalid status: {intent.status}"
                )
                raise ValidationError(
                    "Det skjedde noe galt under behandlingen av betalingen "
                )

            payment_relation.stripe_id = intent.id
            payment_relation.save()

            return payment_relation

        except stripe.error.CardError as err:
            error = err.json_body.get("error", {})
            logger.error(
                f"Stripe charge for {request.user} failed with card_error: {error}"
            )
            raise serializers.ValidationError(error) from err

        except stripe.error.StripeError as error:
            logger.error(f"An error occurred during the Stripe charge: {error}")
            raise serializers.ValidationError(error) from error

    class Meta:
        model = PaymentRelation
        fields = (
            "id",
            "payment",
            "payment_price",
            "payment_method_id",
            "user",
            "status",
            "payment_intent_secret",
            "is_refundable",
            "is_refundable_reason",
        )
        read_only_fields = ("id", "payment_intent_secret", "status")


class PaymentRelationUpdateSerializer(serializers.ModelSerializer):
    payment_intent_id = serializers.CharField(
        write_only=True, required=True, allow_blank=False
    )

    def update(self, instance: PaymentRelation, validated_data):
        # Update should only be used to confirm a payment relation. PENDING is the first stage of a payment.
        if instance.status != status.PENDING:
            raise ValidationError("Denne betalingen er allerede betalt og bekreftet")

        # Remove data, as we only want to use it to potentially write data derived from it
        payment_intent_id = validated_data.pop("payment_intent_id")

        try:
            stripe.api_key = instance.payment.stripe_private_key
            intent = stripe.PaymentIntent.confirm(payment_intent_id)

            # If the status is still not confirmed we update the transaction with a new secret key to handle.
            if (
                intent.status == "requires_source_action"
                and intent.next_action.type == "use_stripe_sdk"
            ):
                return super().update(
                    instance,
                    {**validated_data, "payment_intent_secret": intent.client_secret},
                )
            # If the payment is successfully confirmed we update the status of the transaction to SUCCEEDED.
            elif intent.status == "succeeded":
                return super().update(
                    instance, {**validated_data, "status": status.SUCCEEDED}
                )

            else:
                logger.error(
                    f"Payment intent returned an invalid status: {intent.status}"
                )
                raise ValidationError(
                    "Det skjedde noe galt under behandlingen av betalingsbekreftelsen "
                )

        except stripe.error.CardError as error:
            logger.error(
                f"An error occurred during confirmation of "
                f"PyamentRelation: {instance.id} by user: {instance.user}",
                error,
            )
            raise ValidationError(
                "Det skjedde en feil under bekreftelsen av betalingen."
            ) from error

    class Meta:
        model = PaymentRelation
        fields = (
            "payment_intent_id",
            "id",
            "payment_intent_secret",
            "status",
            "payment",
            "payment_price",
            "is_refundable",
            "is_refundable_reason",
        )
        read_only_fields = (
            "id",
            "payment_intent_secret",
            "status",
            "payment",
            "payment_price",
        )
