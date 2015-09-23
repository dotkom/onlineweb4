from django import forms
from django.forms import ModelForm
from feedme.models import Order, OrderLine, ManageOrderLimit, ManageOrders, Restaurant, ManageBalance, Poll, Answer


class OrderLineForm(ModelForm):
    name = 'orderline'
    price = forms.IntegerField(label='Total price', widget=forms.TextInput(attrs={'placeholder': '9001'}))
    extras = forms.CharField(label='Extras/comments', widget=forms.TextInput(
            attrs={'list': 'extras_tags'},
    ))

    class Meta:
        model = OrderLine
        exclude = ('order', 'creator', 'paid_for')

    def __init__(self, *args, **kwargs):
        super(OrderLineForm, self).__init__(*args, **kwargs)
        self.fields['users'].empty_label = None


class OrderForm(ModelForm):
    name = u'order'

    class Meta:
        model = Order
        fields = ('date', )


class ManageOrderForm(ModelForm):
    name = u'orders'

    class Meta:
        model = ManageOrders
        fields = '__all__'


class ManageBalanceForm(ModelForm):
    name = u'transactions'

    class Meta:
        model = ManageBalance
        fields = '__all__'


class ManageOrderLimitForm(ModelForm):
    name = u'order limit'

    class Meta:
        model = ManageOrderLimit
        fields = '__all__'


class NewOrderForm(ModelForm):
    name = u'new order'

    class Meta:
        model = Order
        fields = '__all__'


class NewRestaurantForm(ModelForm):
    name = u'new restaurant'

    class Meta:
        model = Restaurant
        fields = '__all__'


class NewPollForm(ModelForm):
    name = 'new poll'

    class Meta:
        model = Poll
        fields = '__all__'


class PollAnswerForm(ModelForm):
    name = 'answer'

    class Meta:
        model = Answer
        exclude = ('user', 'poll')
