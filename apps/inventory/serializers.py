from rest_framework import serializers
from apps.inventory.models import Item
from apps.authentication.models import OnlineUser as User
from apps.payment.models import PaymentTransaction, ItemRelation


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = (
                'pk', 'name', 'price',
            )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
                'pk','first_name', 'last_name', 'saldo',
            )


class ItemRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemRelation
        fields = (
                'item', 'transaction',
            )



class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        items = ItemSerializer()
        fields = (
                'user', 'amount', 'items'
            )