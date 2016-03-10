# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import DetailView, RedirectView, TemplateView

from apps.webshop.forms import OrderForm
from apps.webshop.models import Category, Order, OrderLine, Product, ProductSize


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class CartMixin(LoginRequiredMixin):
    def get_context_data(self, **kwargs):
        context = super(CartMixin, self).get_context_data(**kwargs)
        context['order_line'] = self.current_order_line()
        return context

    def current_order_line(self):
        order_line = OrderLine.objects.filter(user=self.request.user, paid=False).first()
        if not order_line:
            order_line = OrderLine.objects.create(user=self.request.user)
        return order_line


class Home(CartMixin, TemplateView):
    template_name = 'webshop/base.html'

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        context['products'] = Product.objects.filter(active=True)
        return context


class CategoryDetail(CartMixin, DetailView):
    model = Category
    context_object_name = 'category'
    template_name = 'webshop/category.html'


class ProductDetail(CartMixin, DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'webshop/product.html'

    def get_context_data(self, **kwargs):
        context = super(ProductDetail, self).get_context_data(**kwargs)
        context['orderform'] = OrderForm
        context['sizes'] = ProductSize.objects.filter(product=self.get_object())
        return context

    def post(self, request, *args, **kwargs):
        product = self.get_object()

        if product.deadline and product.deadline < timezone.now():
            messages.error(request, "Dette produktet er ikke lenger tilgjengelig.")
            return super(ProductDetail, self).get(request, *args, **kwargs)

        form = OrderForm(request.POST)
        if form.is_valid():
            order_line = self.current_order_line()

            size = form.cleaned_data['size']

            # Checking if product has already been added to cart
            order = order_line.orders.filter(product=product, size=size).first()
            if order:
                # Adding to existing order
                order.quantity += form.cleaned_data['quantity']
            else:
                # Creating new order
                order = Order(
                    product=product, price=product.price,
                    quantity=form.cleaned_data['quantity'],
                    size=size,
                    order_line=order_line)
            order.save()
            return redirect('webshop_checkout')
        else:
            messages.error(request, 'Vennligst oppgi et gyldig antall')
        return super(ProductDetail, self).get(request, *args, **kwargs)


class Checkout(CartMixin, TemplateView):
    template_name = 'webshop/checkout.html'


class RemoveOrder(CartMixin, RedirectView):
    pattern_name = 'webshop_checkout'

    def post(self, request, *args, **kwargs):
        order_line = self.current_order_line()
        order_id = request.POST.get('id')
        if order_id:
            Order.objects.filter(order_line=order_line, id=order_id).delete()
        else:
            Order.objects.filter(order_line=order_line).delete()
        return super(RemoveOrder, self).post(request, *args, **kwargs)
