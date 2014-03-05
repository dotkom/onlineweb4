from django.forms import ModelForm
from models import Pizza, Order, OrderLine, ManageOrderLimit, ManageOrderLines, ManageUsers

class PizzaForm(ModelForm):
    name ='pizza'

    class Meta:
        model = Pizza
        exclude = ('order_line', 'user')
       
    def __init__(self, *args, **kwargs):
        super(PizzaForm, self).__init__(*args, **kwargs)
        self.fields['buddy'].empty_label = None 

class OrderForm(ModelForm):
    name=u'order'

    class Meta:
        model = Order
        fields = ('content' ,)



class ManageOrderLinesForm(ModelForm):
    name=u'orders'

    class Meta:
        model = ManageOrderLines

class ManageUsersForm(ModelForm):
    name=u'users'

    class Meta:
        model = ManageUsers

class ManageOrderLimitForm(ModelForm):
    name=u'order limit'

    class Meta:
        model = ManageOrderLimit

class NewOrderLineForm(ModelForm):
    name=u'new order'

    class Meta:
        model = OrderLine
        fields = ('date',)


