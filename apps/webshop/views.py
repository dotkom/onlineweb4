from django.views.generic import TemplateView, DetailView
from apps.webshop.models import Category, Product, Order, OrderLine


class CartMixin(object):
    def get_context_data(self, **kwargs):
        context = super(CartMixin, self).get_context_data(**kwargs)
        context['order_line'] = self.current_order_line()
        return context

    def current_order_line(self):
        order_line = OrderLine.objects.filter(user=self.request.user).first()
        if not order_line:
            order_line = OrderLine.objects.create(user=self.request.user)
        return order_line


class Home(CartMixin, TemplateView):
    template_name = 'webshop/base.html'

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class CategoryDetail(CartMixin, DetailView):
    model = Category
    context_object_name = 'category'
    template_name = 'webshop/category.html'


class ProductDetail(CartMixin, DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'webshop/product.html'


class Checkout(TemplateView):
    pass
