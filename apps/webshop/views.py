from django.views.generic import TemplateView, DetailView
from apps.webshop.models import Category, Product


class Home(TemplateView):
    template_name = 'webshop/webshop.html'

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class CategoryDetail(DetailView):
    model = Category
    context_object_name = 'category'
    template_name = 'webshop/category.html'


class ProductDetail(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'webshop/product.html'


class Checkout(TemplateView):
    pass
