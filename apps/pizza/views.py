from django.contrib import messages
from django.conf import settings

from django.shortcuts import render, get_object_or_404, redirect
from apps.pizza.models import OrderLine, Pizza, Order, Saldo, ManageOrderLimit
from forms import PizzaForm, OrderForm,  ManageOrderLinesForm, ManageOrderLimitForm, NewOrderLineForm, ManageUsersForm
from django.contrib.auth.decorators import user_passes_test
from datetime import date, timedelta
from django.contrib.auth import get_user_model

from apps.authentication.models import OnlineUser as User

@user_passes_test(lambda u: u.groups.filter(name=settings.PIZZA_GROUP).count() == 1)
def pizza_index(request):
    order_line = get_order_line()
    return render(request, 'pizza/index.html', {'order_line' : order_line, 'order_num' : order_line.pizza_set.count(), 'is_admin' : is_admin(request)})

@user_passes_test(lambda u: u.groups.filter(name=settings.PIZZA_GROUP).count() == 1)
def pizza_new(request, pizza_id=None):
    if pizza_id == None:
        pizza = Pizza()
    else:
        pizza = get_object_or_404(Pizza, pk=pizza_id)

    if request.method == 'POST':
        form = PizzaForm(request.POST, instance=pizza)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.order_line = get_order_line()
            if form.need_buddy:
                form.buddy = request.user
            
            if check_pizza_order(request, form, pizza_id):
                form.save()
                return redirect(pizza_index)
            else:
                form = PizzaForm(request.POST, auto_id=True)
        else:
            form = PizzaForm(request.POST, auto_id=True)
    else:
        if pizza_id:
            form = PizzaForm(instance=pizza)
            form.fields["buddy"].queryset = get_order_line().free_users(pizza.buddy, pizza.user)
        else: 
            form = PizzaForm(instance=pizza, initial={'buddy' : request.user})
            form.fields["buddy"].queryset = get_order_line().free_users()
    
    return render(request, 'pizza/orderview.html', {'form' : form, 'is_admin' : is_admin(request)})

def pizza_edit(request, pizza_id):
    pizza = get_object_or_404(Pizza, pk=pizza_id)
    if not is_in_current_order('pizza', pizza_id):
        messages.error(request, 'you can not edit pizzas from old orders')
    elif pizza.user != request.user and pizza.buddy != request.user:
        messages.error(request, 'You need to be the creator or the buddy')
        return redirect(pizza_index)
    return pizza_new(request, pizza_id)

def pizza_delete(request, pizza_id):
    pizza = get_object_or_404(Pizza, pk=pizza_id)
    if not is_in_current_order('pizza', pizza_id):
        messages.error(request, 'you can not delete pizzas from old orders')
    elif pizza.user == request.user or pizza.buddy == request.user:
        pizza.delete()
        messages.success(request,'Pizza deleted')
    else:
        messages.error(request, 'You need to be the creator or the buddy')
    return redirect(pizza_index)

@user_passes_test(lambda u: u.groups.filter(name=settings.PIZZA_GROUP).count() == 1)
def pizza_new_order(request, order_id=None):
    if order_id:
        order = get_object_or_404(Order, pk=order_id)
    else:
        order = Order()

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.order_line = get_order_line()
            form.save()
            messages.success(request, 'Order added')
            return redirect(pizza_index)
        
        form = OrderForm(request.POST)
    else:
        form = OrderForm(instance=order)

    return render(request, 'pizza/orderview.html', {'form' : form, 'is_admin' : is_admin(request)})

def pizza_order_delete(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if not is_in_current_order('order', order_id):
        messages.error(request, 'you can not delete orders from old orders')
    elif order.user == request.user:
        order.delete()
        messages.success(request,'Order deleted')
    else:
        messages.error(request, 'You need to be the creator')
    return redirect(pizza_index)


def pizza_order_edit(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if not is_in_current_order('order', order_id):
        messages.error(request, 'you can not edit orders from old orders')
    elif order.user != request.user:
        messages.error(request, 'You need to be the creator to edit orders')
    else:
        return pizza_new_order(request, order_id)
    return redirect(pizza_index)


@user_passes_test(lambda u: u.groups.filter(name=settings.PIZZA_GROUP).count() == 1)
def pizza_join(request, pizza_id):
    pizza = get_object_or_404(Pizza, pk=pizza_id)
    if user_is_taken(request.user):
        messages.error(request, 'You are already a part of a pizza')
    elif not is_in_current_order('pizza', pizza_id):
        messages.error(request, 'you can not join pizzas from old orders')
    elif not pizza.need_buddy:
        messages.error(request, 'You can\'t join that pizza')
    elif not request.user.saldo_set.all():
        messages.error(request, 'No saldo connected to the user')
    elif request.user.saldo_set.get().saldo < get_order_limit().order_limit:
        messages.error(request, 'You have insufficent funds. Current limit : ' + str(get_order_limit().order_limit))
    else:
        pizza.buddy = request.user
        pizza.need_buddy = False
        pizza.save()
        messages.success(request, 'Success!')
    return redirect(pizza_index) 

# ADMIN

@user_passes_test(lambda u: u.groups.filter(name=settings.PIZZA_ADMIN_GROUP).count() == 1)
def pizza_admin_new(request):
    if request.method == 'POST':
        form = NewOrderLineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'New order line added')
            return redirect(pizza_admin_new)
    else:
        form = NewOrderLineForm()
        form.fields["date"].initial = get_next_tuesday()

    return render(request, 'pizza/admin.html', {'form' : form })

@user_passes_test(lambda u: u.groups.filter(name=settings.PIZZA_ADMIN_GROUP).count() == 1)
def pizza_admin_limit(request):
    limit = get_order_limit()
    if request.method == 'POST':
        form = ManageOrderLimitForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            limit.order_limit = data['order_limit']
            limit.save()
            messages.success(request,'Order limit changed')
            return redirect(pizza_admin_limit)
    else:
        form = ManageOrderLimitForm(instance=limit)

    return render(request, 'pizza/admin.html', {'form' : form })

@user_passes_test(lambda u: u.groups.filter(name=settings.PIZZA_ADMIN_GROUP).count() == 1)
def pizza_admin_users(request):
    if request.method == 'POST':
        form = ManageUsersForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            handle_deposit(data)
            messages.success(request, 'Deposit successful')
            return redirect(pizza_admin_users)
    else:
        validate_saldo()
        form = ManageUsersForm()
        form.fields["users"].queryset = get_pizza_users()
    
    return render(request, 'pizza/admin.html', {'form' : form })

@user_passes_test(lambda u: u.groups.filter(name=settings.PIZZA_ADMIN_GROUP).count() == 1)
def pizza_admin_orders(request):
    if request.method == 'POST':
        form = ManageOrderLinesForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            handle_payment(request, data)
            return redirect(pizza_admin_orders)
        else:
            form = ManageOrderLinesForm(request.POST)
    else:
        form = ManageOrderLinesForm()
    
    unhandeled_orders = OrderLine.objects.filter(total_sum=0)
    form.fields["order_lines"].queryset = unhandeled_orders
    return render(request, 'pizza/admin.html', {'form' : form, 'order_lines' : unhandeled_orders})

def get_order_limit():
    order_limit = ManageOrderLimit.objects.all()
    if order_limit:
        order_limit = ManageOrderLimit.objects.get(pk=1)
    else:
        order_limit = ManageOrderLimit()
    return order_limit

#methods

def user_is_taken(user):
    return user in get_order_line().used_users()

def check_pizza_order(request, form, pizza_id=None):
    validate_saldo()
    order_limit = get_order_limit().order_limit
    saldo = form.user.saldo_set.get()

    if not pizza_id:
        if user_is_taken(form.user):
            messages.error(request, form.user.username + ' has already ordered a pizza')
            return False
        if user_is_taken(form.buddy):
            messages.error(request, form.buddy.username + ' has already ordered a pizza')
            return False
    if form.user == form.buddy:
        if saldo.saldo < (order_limit * 2):
           messages.error(request, u'' + form.user.username + ' has insufficient funds. Current limit: ' + str(order_limit) )
           return False
    else:
        if saldo.saldo < order_limit:
            messages.error(request,u'' + form.user.username + ' has insufficient funds. Current limit: ' + str(order_limit) )
            return False

        saldo = form.buddy.saldo_set.get()
        if saldo.saldo < order_limit:
            messages.error(request,u'' + form.buddy.username + ' has insufficient funds. Current limit: ' + str(order_limit) )
            return False
    messages.success(request, 'Pizza added')
    return True

def handle_payment(request, data):
    order_line = data['order_lines']
    total_sum = data['total_sum']
    users = order_line.used_users()
    if users:
        divided_sum = (total_sum / len(users)) * -1
        handle_saldo(users, divided_sum)
        order_line.total_sum = total_sum
        order_line.save()
        messages.success(request, 'Payment handeled')
    else:
        messages.error(request, 'Selected order contains no users')

def handle_deposit(data):
    users = data['users']
    deposit = data['add_value']

    handle_saldo(users, deposit) 
    
def handle_saldo(users, value):
    for user in users:
        saldo = user.saldo_set.get()
        saldo.saldo += value
        saldo.save()

def validate_saldo():
    users = get_pizza_users()
    for user in users:
        saldo = user.saldo_set.all()
        if not saldo:
            saldo = Saldo()
            saldo.user = user
            saldo.save()
        
def get_next_tuesday():
    today = date.today()
    day = today.weekday()
    if day < 1:
        diff = timedelta(days=(1 - day))
    elif day > 1:
        diff = timedelta(days=(7- day + 1))
    else:
        diff = timedelta(days=0)
    
    return today + diff

def is_admin(request):
    return request.user in User.objects.filter(groups__name=settings.PIZZA_ADMIN_GROUP)

def get_pizza_users():
   return User.objects.filter(groups__name=settings.PIZZA_GROUP)

def get_order_line():
    if OrderLine.objects.all():
        return OrderLine.objects.all().latest()
    else:
        return False

def is_in_current_order(order_type, order_id):
    order_line = get_order_line()
    if order_type == 'pizza':
        pizza = get_object_or_404(Pizza, pk=order_id)
        return pizza in order_line.pizza_set.all()
    elif order_type == 'order':
        order = get_object_or_404(Order, pk=order_id)
        return order in order_line.order_set.all()
    else:
        return False
