from django import forms

from apps.webshop import models


class OrderForm(forms.ModelForm):
    class Meta:
        model = models.Order
        fields = ["quantity", "size"]
