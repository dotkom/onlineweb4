from apps.webshop import models
from django import forms


class OrderForm(forms.ModelForm):
    class Meta:
        model = models.Order
        fields = ['quantity', 'size']
