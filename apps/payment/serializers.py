import logging

import stripe
from django.conf import settings
from rest_framework import serializers

from apps.payment.models import (Payment, PaymentDelay, PaymentPrice, PaymentRelation,
                                 PaymentTransaction)

logger = logging.getLogger(__name__)


class PaymentPriceReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentPrice
        fields = ('id', 'price', 'description',)
        read_only = True


class PaymentReadOnlySerializer(serializers.ModelSerializer):
    payment_prices = PaymentPriceReadOnlySerializer(many=True, read_only=True)

    class Meta:
        model = Payment
        fields = ('id', 'payment_prices', 'description', 'stripe_public_key',)
        read_only = True


class PaymentRelationReadOnlySerializer(serializers.ModelSerializer):
    payment = PaymentReadOnlySerializer(read_only=True)
    payment_price = PaymentPriceReadOnlySerializer(read_only=True)

    class Meta:
        model = PaymentRelation
        fields = ('payment', 'payment_price', 'datetime', 'refunded')
        read_only = True


class PaymentDelayReadOnlySerializer(serializers.ModelSerializer):
    payment = PaymentReadOnlySerializer()

    class Meta:
        model = PaymentDelay
        fields = ('payment', 'valid_to', 'active')
        read_only = True


class PaymentRelationCreateSerializer(serializers.ModelSerializer):
    """
    Relates the user, to a payment, stripe charge and price
    """
    payment = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=Payment.objects.all(),
    )
    payment_price = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=PaymentPrice.objects.all(),
    )
    stripe_token = serializers.CharField(write_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate(self, data):
        payment = data.get('payment')
        payment_price = data.get('payment_price')
        valid_price_pks = [price.pk for price in PaymentPrice.objects.filter(payment=payment)]

        if payment_price.id not in valid_price_pks:
            raise serializers.ValidationError('Supplied payment price is not valid for the supplied payment')

        return data

    def create(self, validated_data):
        """
        Overwrite create to handle the stripe charge before the relation is created.
        """
        request = self.context.get('request')
        user = request.user

        payment: Payment = validated_data.get('payment')
        payment_price: PaymentPrice = validated_data.get('payment_price')

        if not payment.is_user_allowed_to_pay(user):
            raise serializers.ValidationError('Du har ikke tilgang til å betale for denne betalingen')

        """ Get stripe token and remove it from the data that from the create data """
        stripe_token = validated_data.pop('stripe_token')

        logger.info(f'Set up Stripe for payment:{payment.id}, user:{request.user.id}, '
                    f'price: {payment_price.price} kr')
        try:
            """ Validate and make the Charge with the Stripe token """
            charge = stripe.Charge.create(
                amount=payment_price.price * 100,  # Price is multiplied with 100 because the amount is in øre
                currency="nok",
                card=stripe_token,
                description=f'{payment.description()} - {request.user.email}',
                api_key=payment.stripe_private_key,
            )

            created_payment_relation = super().create({
                'stripe_id': charge.id,
                **validated_data,
            })

            """ Handle the completed payment. Remove delays, suspensions and marks """
            payment.handle_payment(request.user)

            return created_payment_relation

        except stripe.error.CardError as err:
            error = err.json_body.get('error', {})
            logger.error(f'Stripe charge for {request.user} failed with card_error: {error}')
            raise serializers.ValidationError(error)

        except stripe.error.StripeError as error:
            logger.error(f'An error occurred during the Stripe charge: {error}')
            raise serializers.ValidationError(error)

        return None

    class Meta:
        model = PaymentRelation
        fields = ('id', 'payment', 'payment_price', 'stripe_token', 'user',)


class PaymentTransactionReadOnlySerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    def get_items(self, obj: PaymentTransaction):
        return obj.get_items()

    def get_description(self, obj: PaymentTransaction):
        return obj.get_description()

    class Meta:
        model = PaymentTransaction
        fields = ('amount', 'used_stripe', 'datetime', )
        read_only = True


class PaymentTransactionCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    stripe_token = serializers.CharField(write_only=True)
    used_stripe = serializers.HiddenField(default=True)
    amount = serializers.IntegerField(required=True)

    def validate_amount(self, amount):
        valid_amounts = [100, 200, 500]
        if amount not in valid_amounts:
            raise serializers.ValidationError(f'{amount} er ikke en gyldig betalingspris')

        return amount

    def create(self, validated_data):
        request = self.context.get('request')

        amount = validated_data.get('amount')
        stripe_token = validated_data.pop('stripe_token')

        logger.info(f'User: {request.user} attempting to add {amount} to saldo')
        try:
            """ Use Trikom key for additions to user saldo """
            stripe_private_key = settings.STRIPE_PRIVATE_KEYS['trikom']
            stripe.Charge.create(
                amount=amount * 100,  # Price is multiplied with 100 because the amount is in øre
                currency="nok",
                card=stripe_token,
                description=f'Saldo deposit - {request.user.email}',
                api_key=stripe_private_key,
            )
            return super().create(validated_data)

        except stripe.error.CardError as err:
            error = err.json_body.get('error', {})
            logger.error(f'Stripe charge for {request.user} failed with card_error: {error}')
            raise serializers.ValidationError(error)

        except stripe.error.StripeError as error:
            logger.error(f'An error occurred during the Stripe charge: {error}')
            raise serializers.ValidationError(error)

        return None

    class Meta:
        model = PaymentTransaction
        fields = ('id', 'stripe_token', 'amount', 'used_stripe', 'user',)
