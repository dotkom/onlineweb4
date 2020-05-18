# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, RedirectView, TemplateView
from rest_framework import permissions, viewsets

from apps.authentication.models import OnlineUser as User
from apps.common.rest_framework.mixins import MultiSerializerMixin
from apps.webshop.forms import OrderForm
from apps.webshop.models import Category, Order, OrderLine, Product, ProductSize
from apps.webshop.serializers import (
    OrderCreateSerializer,
    OrderLineCreateSerializer,
    OrderLineReadOnlySerializer,
    OrderReadOnlySerializer,
    OrderUpdateSerializer,
    ProductReadOnlySerializer,
)


class LoginRequiredMixin:
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class CartMixin:
    def get_context_data(self, **kwargs):
        context = super(CartMixin, self).get_context_data(**kwargs)
        context["order_line"] = self.current_order_line()
        return context

    def current_order_line(self):
        user: User = self.request.user
        return OrderLine.get_current_order_line_for_user(user)


class BreadCrumb:
    """Dynamically generated breadcrumbs using name and url"""

    def get_breadcrumbs(self):
        """Create breadcrumb for the main webshop page

        Returns:
            list: list of breadcrumbs
        """
        breadcrumbs = [{"name": "Webshop", "url": reverse_lazy("webshop_home")}]
        return breadcrumbs

    def get_context_data(self, **kwargs):
        """Add breadcrumbs to context"""
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = self.get_breadcrumbs()
        return context


class WebshopMixin(CartMixin, BreadCrumb):
    pass


class Home(WebshopMixin, TemplateView):
    template_name = "webshop/base.html"

    def get_breadcrumbs(self):
        return None

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        context["products"] = Product.objects.filter(active=True)
        return context


class CategoryDetail(WebshopMixin, DetailView):
    model = Category
    context_object_name = "category"
    template_name = "webshop/category.html"

    def get_breadcrumbs(self):
        breadcrumbs = super().get_breadcrumbs()
        breadcrumbs.append({"name": self.get_object()})
        return breadcrumbs


class ProductDetail(WebshopMixin, DetailView):
    model = Product
    context_object_name = "product"
    template_name = "webshop/product.html"

    def get_breadcrumbs(self):
        breadcrumbs = super().get_breadcrumbs()
        breadcrumbs.append({"name": self.get_object()})
        return breadcrumbs

    def get_context_data(self, **kwargs):
        context = super(ProductDetail, self).get_context_data(**kwargs)
        context["orderform"] = OrderForm
        context["sizes"] = ProductSize.objects.filter(product=self.get_object())
        return context

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        product = self.get_object()
        if product.deadline and product.deadline < timezone.now():
            messages.error(request, "Dette produktet er ikke lenger tilgjengelig.")
            return super(ProductDetail, self).get(request, *args, **kwargs)

        if not product.in_stock():
            messages.error(request, "Dette produktet er utsolgt.")
            return super().get(request, *args, **kwargs)

        form = OrderForm(request.POST)
        if form.is_valid():
            order_line = self.current_order_line()

            size = form.cleaned_data["size"]
            quantity = form.cleaned_data["quantity"]

            if not product.enough_stock(quantity, size):
                messages.error(request, "Det er ikke nok produkter på lageret.")
                return super().get(request, *args, **kwargs)

            # Checking if product has already been added to cart
            order = order_line.orders.filter(product=product, size=size).first()
            if order:
                # Adding to existing order
                order.quantity += quantity
            else:
                # Creating new order
                order = Order(
                    product=product,
                    price=product.price,
                    quantity=quantity,
                    size=size,
                    order_line=order_line,
                )
            order.save()
            return redirect("webshop_checkout")
        else:
            messages.error(request, "Vennligst oppgi et gyldig antall")
        return super(ProductDetail, self).get(request, *args, **kwargs)


class Checkout(LoginRequiredMixin, WebshopMixin, TemplateView):
    template_name = "webshop/checkout.html"

    def get_breadcrumbs(self):
        breadcrumbs = super().get_breadcrumbs()
        breadcrumbs.append({"name": "Sjekk ut"})
        return breadcrumbs

    def get(self, request, *args, **kwargs):
        order_line = self.current_order_line()
        if order_line:
            invalid_orders = order_line.orders.filter(
                Q(product__active=False)
                | Q(product__deadline__lt=timezone.now())
                | Q(product__stock=0)
            )

            self.remove_inactive_orders(invalid_orders)

        return super(Checkout, self).get(request, *args, **kwargs)

    def remove_inactive_orders(self, orders):
        for order in orders:
            if order.product.stock == 0:
                message = """Det er ingen {} på lager og varen er fjernet
                             fra din handlevogn.""".format(
                    order.product.name
                )
            else:
                message = """{} er ikke lenger tilgjengelig for kjøp og
                             er fjernet fra din handlevogn.""".format(
                    order.product.name
                )
            messages.add_message(self.request, messages.INFO, message)
            order.delete()


class RemoveOrder(LoginRequiredMixin, WebshopMixin, RedirectView):
    pattern_name = "webshop_checkout"

    def post(self, request, *args, **kwargs):
        order_line = self.current_order_line()
        order_id = request.POST.get("id")
        if order_id:
            Order.objects.filter(order_line=order_line, id=order_id).delete()
        else:
            Order.objects.filter(order_line=order_line).delete()
        return super(RemoveOrder, self).post(request, *args, **kwargs)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(active=True)
    permission_classes = (permissions.AllowAny,)
    serializer_class = ProductReadOnlySerializer


class OrderViewSet(MultiSerializerMixin, viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_classes = {
        "create": OrderCreateSerializer,
        "read": OrderReadOnlySerializer,
        "update": OrderUpdateSerializer,
    }

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(order_line__user=user)


class OrderLineViewSet(MultiSerializerMixin, viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_classes = {
        "read": OrderLineReadOnlySerializer,
        "write": OrderLineCreateSerializer,
    }

    def get_queryset(self):
        user = self.request.user
        return OrderLine.objects.filter(user=user)
