from rest_framework import serializers

from .models import FikenCustomer, FikenOrderLine, FikenSale, FikenSaleAttachment
from .settings import FIKEN_ORG_API_URL


class FikenSaleAttachmentSerializer(serializers.ModelSerializer):
    attachToPayment = serializers.BooleanField(source='attach_to_payment')
    attachToSale = serializers.BooleanField(source='attach_to_sale')

    class Meta:
        model = FikenSaleAttachment
        fields = (
            'filename', 'comment', 'attachToPayment', 'attachToSale',
        )
        read_only = True


class FikenOrderLineSerializer(serializers.ModelSerializer):
    netPrice = serializers.IntegerField(source='net_price')
    vat = serializers.IntegerField(source='vat_price')
    vatType = serializers.CharField(source='vat_type')
    account = serializers.SerializerMethodField()

    def get_account(self, obj: FikenOrderLine):
        return obj.account.code

    class Meta:
        model = FikenOrderLine
        fields = ('netPrice', 'vat', 'vatType', 'account', 'description',)
        read_only = True


class FikenSaleSerializer(serializers.ModelSerializer):
    totalPaid = serializers.IntegerField(source='amount')
    paymentDate = serializers.CharField(source='date')
    paymentAccount = serializers.CharField(source='account')
    customer = serializers.SerializerMethodField()
    lines = FikenOrderLineSerializer(many=True)

    def get_customer(self, obj: FikenSale):
        return f'{FIKEN_ORG_API_URL}/contacts/{obj.customer.fiken_customer_number}'

    class Meta:
        model = FikenSale
        fields = (
            'identifier', 'date', 'kind', 'paid', 'totalPaid', 'lines', 'paymentDate', 'paymentAccount', 'customer',
        )
        read_only = True


class FikenCustomerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phoneNumber = serializers.SerializerMethodField('get_phone_number')
    customer = serializers.SerializerMethodField()

    def get_customer(self, obj: FikenCustomer):
        return True

    def get_name(self, obj: FikenCustomer):
        return obj.user.get_full_name()

    def get_email(self, obj: FikenCustomer):
        return obj.user.primary_email

    def get_phone_number(self, obj: FikenCustomer):
        return obj.user.phone_number

    class Meta:
        model = FikenCustomer
        fields = ('name', 'customer', 'email', 'phoneNumber',)
        read_only = True
