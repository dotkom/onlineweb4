from django.utils import timezone
from rest_framework import serializers

from apps.gallery.serializers import ResponsiveImageSerializer
from apps.payment.serializers import PaymentReadOnlySerializer
from apps.webshop.models import Category, Order, OrderLine, Product, ProductSize


class CategoryReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")
        read_only = True


class ProductSizeReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = ("size", "description", "stock")
        read_only = True


class ProductReadOnlySerializer(serializers.ModelSerializer):
    category = CategoryReadOnlySerializer()
    product_sizes = ProductSizeReadOnlySerializer(many=True)
    images = ResponsiveImageSerializer(many=True)
    related_products = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Product.objects.filter(active=True)
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "category",
            "name",
            "slug",
            "short",
            "description",
            "images",
            "price",
            "stock",
            "deadline",
            "active",
            "product_sizes",
            "related_products",
        )
        read_only = True


class OrderReadOnlySerializer(serializers.ModelSerializer):
    product = ProductReadOnlySerializer()
    size = ProductSizeReadOnlySerializer()

    class Meta:
        model = Order
        fields = ("id", "product", "price", "quantity", "size", "is_valid")
        read_only = True


class CurrentOrderLineDefault(serializers.CurrentUserDefault):
    """
    Gets the currently active order_line for the logged in user
    """

    def __call__(self, serializer_field):
        user = super().__call__(serializer_field)
        return OrderLine.get_current_order_line_for_user(user)


class OrderCreateSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        required=True, queryset=Product.objects.all()
    )
    size = serializers.PrimaryKeyRelatedField(
        default=None, queryset=ProductSize.objects.all()
    )
    order_line = serializers.HiddenField(default=CurrentOrderLineDefault())
    quantity = serializers.IntegerField(min_value=1, max_value=100, default=1)

    def validate_product(self, product: Product):

        if not product.active:
            raise serializers.ValidationError(
                f"Produktet er ikke lenger aktivt og kan ikke kjøpes"
            )

        if timezone.now() > product.deadline:
            raise serializers.ValidationError(
                f"Tidsfristen for å kjøpe produktet har utgått"
            )

        if product.stock == 0:
            raise serializers.ValidationError(
                f"Det er ikke flere varer igjen av produktet"
            )

        return product

    def validate_size(self, size: ProductSize):
        product_id: int = self.initial_data.get("product")
        quantity: int = self.initial_data.get("quantity", 1)

        if product_id:
            product = Product.objects.get(pk=product_id)
            allowed_sizes = product.product_sizes.all()
            has_size = allowed_sizes.count() > 0

            if not has_size and size:
                raise serializers.ValidationError(
                    "Du kan ikke velge en størrelse for dette produktet"
                )

            if has_size and not size:
                raise serializers.ValidationError(
                    "Dette produktet krever at du velger en størrelse"
                )

            if has_size and size not in allowed_sizes:
                raise serializers.ValidationError(
                    f"Den gitte størrelsen er ikke tilgjengelig for dette produktet"
                )

            if not product.enough_stock(quantity, size):
                if not size:
                    raise serializers.ValidationError(
                        f"Det er ikke flere varer igjen av dette produktet"
                    )
                else:
                    raise serializers.ValidationError(
                        f"Det er ikke flere varer igjen av dette produktet in denne størrelsen"
                    )

        return size

    def validate_order_line(self, order_line: OrderLine):
        request = self.context.get("request")

        if order_line.user != request.user:
            raise serializers.ValidationError(
                f"Du kan ikke legge varer til andre brukeres handlevogn"
            )

        return order_line

    def validate(self, data):
        order_line: OrderLine = data.get("order_line")
        product: Product = data.get("product")

        products_in_order_line = [order.product for order in order_line.orders.all()]

        if product in products_in_order_line:
            raise serializers.ValidationError(
                "Dette produktet er allerede i handlevognen din"
            )

        return super().validate(data)

    def create(self, validated_data):
        product: Product = validated_data.get("product")

        order = super().create(
            {
                **validated_data,
                "price": product.price,  # Add the current price of the product as the price of the order
            }
        )

        if not order.is_valid():
            order.delete()
            raise serializers.ValidationError(f"Ordren er ikke gyldig")

        return order

    class Meta:
        model = Order
        fields = (
            "id",
            "product",
            "price",
            "quantity",
            "size",
            "is_valid",
            "order_line",
        )


class OrderUpdateSerializer(serializers.ModelSerializer):
    size = serializers.PrimaryKeyRelatedField(queryset=ProductSize.objects.all())

    def validate_size(self, size: ProductSize):
        product_id: int = self.data.get("product")
        product = Product.objects.get(product_id)
        allowed_sizes = product.product_sizes.all()

        if allowed_sizes.count() > 0 and size not in allowed_sizes:
            raise serializers.ValidationError(
                f"Denne størrelsen er ikke tilgjengelig for dette produktet"
            )

        if not product.enough_stock(size):
            if not size:
                raise serializers.ValidationError(
                    f"Det er ikke flere varer igjen av dette produktet"
                )
            else:
                raise serializers.ValidationError(
                    f"Det er ikke flere varer igjen av dette produktet in denne størrelsen"
                )

        return size

    class Meta:
        model = Order
        fields = ("id", "product", "price", "quantity", "size", "is_valid")
        read_only_fields = ("id", "product", "price", "is_valid")


class OrderLineReadOnlySerializer(serializers.ModelSerializer):
    orders = OrderReadOnlySerializer(many=True)
    payment = serializers.SerializerMethodField()

    def get_payment(self, order_line: OrderLine):
        payment = order_line.payment
        if payment:
            return PaymentReadOnlySerializer(order_line.payment).data
        return None

    class Meta:
        model = OrderLine
        fields = (
            "id",
            "datetime",
            "paid",
            "stripe_id",
            "delivered",
            "orders",
            "subtotal",
            "is_valid",
            "payment",
        )
        read_only = True


class OrderLineCreateSerializer(serializers.ModelSerializer):
    orders = OrderReadOnlySerializer(required=False, many=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate(self, data):
        request = self.context.get("request")
        user_order_lines = OrderLine.objects.filter(user=request.user)

        has_unpaid_order_line = any([not line.paid for line in user_order_lines])
        if has_unpaid_order_line:
            raise serializers.ValidationError(
                f"Du har allerede en handlekurv som ikke er betalt, betal eller slett den for å kunne opprette en ny"
            )

        return super().validate(data)

    class Meta:
        model = OrderLine
        fields = (
            "id",
            "datetime",
            "paid",
            "stripe_id",
            "delivered",
            "orders",
            "subtotal",
            "is_valid",
            "user",
        )
        read_only_fields = (
            "id",
            "datetime",
            "paid",
            "stripe_id",
            "delivered",
            "subtotal",
            "is_valid",
        )
