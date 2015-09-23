from datetime import date, timedelta

from django.contrib import messages
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404, redirect

from feedme.models import OrderLine, Order, ManageOrderLimit, Restaurant, Balance, Transaction, Poll, Answer
from feedme.forms import OrderLineForm, OrderForm, ManageOrderForm, ManageOrderLimitForm, NewOrderForm, NewRestaurantForm, ManageBalanceForm, NewPollForm, PollAnswerForm

try:
    # Django 1.7 way for importing custom user
    from django.contrib.auth import AUTH_USER_MODEL
    User = get_user_model()
except ImportError:
    try:
        # Django 1.6 way for importing custom user, will crash in Django 1.7
        from django.contrib.auth import get_user_model
        User = get_user_model()
    except AppRegistryNotReady:
        # If all else fails, import default user model -- please report this bug
        from django.contrib.auth.models import User


# Index
# @user_passes_test(lambda u: u.groups.filter(name=settings.FEEDME_GROUP).count() == 1)
def index(request):
    order = get_order()
    poll = get_poll()
    a_id = None
    if str(request.user) != 'AnonymousUser':
        if Answer.objects.filter(poll=poll, user=request.user).count() == 1:
            a_id = Answer.objects.get(poll=poll, user=request.user)
    if request.method == 'POST':
        if request.POST['act'] == 'vote':
            if a_id is not None:
                form = PollAnswerForm(request.POST, instance=a_id)
            else:
                form = PollAnswerForm(request.POST)
            if form.is_valid():
                answer = form.save(commit=False)
                answer.user = request.user
                answer.poll = poll
                answer.save()
                messages.success(request, 'Voted for %s' % answer.answer)
                return redirect(index)
        elif request.POST['act'] == 'log_in':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect(index)
                else:
                    pass # tell user it failed
            else:
                pass # failed passwordsd
    r = dict(
        order=order,
        restaurants=Restaurant.objects.all(),
        is_admin=is_admin(request),
        can_join=not in_other_orderline(request.user),
    )
    if poll is not None:
        r['poll'] = poll
        if a_id is None:
            r['answer'] = PollAnswerForm()
        else:
            r['answer'] = PollAnswerForm(instance=a_id)
        r['results'] = poll.get_result()
    return render(request, 'index.html', r)


def log_in(request):
    return redirect(index)

# View order
@user_passes_test(lambda u: u.groups.filter(name=settings.FEEDME_GROUP).count() == 1)
def orderview(request, order_id=None):
    if order_id:
        order = get_object_or_404(Order, pk=order_id)
    else:
        order = Order()

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form = form.save(commit=False)
            form.creator = request.user
            form.order_line = get_order()
            form.save()
            messages.success(request, 'Orderline added')
            return redirect(index)

        form = OrderForm(request.POST)
    else:
        form = OrderForm(instance=order)

    return render(request, 'orderview.html', {'form': form, 'is_admin': is_admin(request)})


# New / edit order line
def orderlineview(request, orderline_id=None):
    new_or_existing_orderline = 'new'
    if orderline_id is None:
        orderline = OrderLine()
        creator = None
    else:
        orderline = get_object_or_404(OrderLine, pk=orderline_id)
        new_or_existing_orderline = 'existing'
        creator = orderline.creator

    if request.method == 'POST':
        form = OrderLineForm(request.POST, instance=orderline)
        if form.is_valid():
            new_orderline = form.save(commit=False)
            if creator is not None:
                new_orderline.creator = creator
            else:
                new_orderline.creator = request.user
            new_orderline.order = get_order()
            users = manually_parse_users(form)
            if check_orderline(request, new_orderline, orderline_id, users):
                new_orderline.save()
                form.save_m2m()  # Manually save the m2m relations when using commit=False
                if new_or_existing_orderline == 'new':
                    messages.success(request, "Orderline added")
                else:
                    messages.success(request, "Orderline edited")
                new_orderline.users.add(new_orderline.creator)
                return redirect(index)
            else:
                messages.error(request, "Orderline validation failed, please verify your data and try again.")  # @ToDo More useful errors
                new_orderline = OrderLineForm(request.POST, auto_id=True)
        else:
            new_orderline = OrderLineForm(request.POST, auto_id=True)
    else:
        form = OrderLineForm(instance=orderline)
        form.fields["users"].queryset = get_order().available_users().exclude(id=request.user.id)
    return render(request, 'orderview.html', {'form': form, 'is_admin': is_admin(request)})


# Edit order line
def edit_orderline(request, orderline_id):
    orderline = get_object_or_404(OrderLine, pk=orderline_id)
    if not is_in_current_order('orderline', orderline_id):
        messages.error(request, 'you can not edit orderlines from old orders')
    elif request.user != orderline.creator and request.user not in orderline.users.all():
        messages.error(request, 'You need to be the creator')
        return redirect(index)
    return orderlineview(request, orderline_id)


# Delete order line
def delete_orderline(request, orderline_id):
    orderline = get_object_or_404(OrderLine, pk=orderline_id)
    if not is_in_current_order('orderline', orderline_id):
        messages.error(request, 'You can not delete orderlines from old orders')
    elif orderline.creator == request.user:
        orderline.delete()
        messages.success(request, 'Orderline deleted')
    else:
        messages.error(request, 'You need to be the creator or the buddy')
    return redirect(index)


@user_passes_test(lambda u: u.groups.filter(name=settings.FEEDME_GROUP).count() == 1)
def join_orderline(request, orderline_id):
    orderline = get_object_or_404(OrderLine, pk=orderline_id)
    # @TODO if not buddy system enabled, disable join
    if not is_in_current_order('orderline', orderline_id):
        messages.error(request, 'You can not join orderlines from old orders')
    elif in_other_orderline(request.user):
        messages.error(request, 'You cannot be in multiple orderlines')
    elif orderline.order.use_validation and not validate_user_funds(request.user, (orderline.price / (orderline.users.count() + 1))):  # Adds us to the test aswell
        messages.error(request, 'You need cashes')
    else:
        orderline.users.add(request.user)
        orderline.save()
        messages.success(request, 'Joined orderline')
    return redirect(index)


@user_passes_test(lambda u: u.groups.filter(name=settings.FEEDME_GROUP).count() == 1)
def leave_orderline(request, orderline_id):
    orderline = get_object_or_404(OrderLine, pk=orderline_id)
    if not is_in_current_order('orderline', orderline_id):
        messages.error(request, 'You cannot leave old orders')
    elif request.user not in orderline.users.all():
        messages.error(request, 'You cannot leave since you are not in the users')
    else:
        orderline.users.remove(request.user)
        orderline.save()
        messages.success(request, 'Left orderline')
    return redirect(index)


# ADMIN


# New order
@user_passes_test(lambda u: u.groups.filter(name=settings.FEEDME_ADMIN_GROUP).count() == 1)
def new_order(request):
    if request.method == 'POST':
        form = NewOrderForm(request.POST)
        if form.is_valid():
            form.save()
            poll = Poll.get_active()
            if poll:
                poll.deactivate()
            messages.success(request, 'New order added')
            return redirect(index)
    else:
        form = NewOrderForm()
        if Poll.objects.count() > 0:
            poll = Poll.get_active()
            if poll:
                form.fields['restaurant'].initial = poll.get_winner()
        form.fields["date"].initial = get_next_wednesday()

    return render(request, 'admin.html', {'form': form, 'is_admin': is_admin(request)})


# Manage users (deposit, withdraw, overview)
@user_passes_test(lambda u: u.groups.filter(name=settings.FEEDME_ADMIN_GROUP).count() == 1)
def manage_users(request, balance=None):
    if request.method == 'POST':
        if balance is None:
            balance = get_or_create_balance(request.user)
        else:
            balance = get_object_or_404(Balance, balance)
        form = ManageBalanceForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            handle_deposit(data)
            messages.success(request, 'Deposit successful')
            return redirect(manage_users)
    else:
        form = ManageBalanceForm()
    users = []
    for user in get_orderline_users():
        get_or_create_balance(user)
        users.append(user)
    form.fields["user"].queryset = get_orderline_users()

    return render(request, 'manage_users.html', {'form': form, 'users': users, 'is_admin': is_admin(request)})


# Manage order (payment handling)
@user_passes_test(lambda u: u.groups.filter(name=settings.FEEDME_ADMIN_GROUP).count() == 1)
def manage_order(request):
    if request.method == 'POST':
        form = ManageOrderForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            order = get_object_or_404(Order, pk=data['orders'].id)
            if 'active_order_submit' in request.POST:
                order.active = request.POST['active_order_submit'] == 'Activate'
                order.save()
                return redirect(manage_order)
            orderlines = order.orderline_set.all()
            total_price = order.extra_costs
            for orderline in orderlines:
                orderline.users.add(orderline.creator)
                orderline.each = orderline.get_total_price() / (orderline.users.count())
                total_price += orderline.price
            if request.POST['act'] == 'Load':
                return render(request, 'manage_order.html', {'form': form, 'is_admin': is_admin(request), 'order': order, 'orderlines': orderlines, 'total_price': total_price})
            elif request.POST['act'] == 'Edit':
                for rq in request.POST:
                    if 'edit_orderline_price' in rq:
                        i = rq.split('-')[1]
                        ol = orderlines.get(id=i)
                        change = int(request.POST[rq])
                        if ol.price != change:
                            ol.price = change
                            ol.save()
                            messages.success(request, 'Changed price for %(ol)s to %(price)s' % {'ol': ol, 'price': ol.price})
                return redirect(manage_order)
            elif request.POST['act'] == 'Pay':
                handle_payment(request, order)
                return redirect(manage_order)
        else:
            form = ManageOrderForm(request.POST)
    else:
        form = ManageOrderForm()

    orders = Order.objects.all()
    orders_price = {}
    active_orders = Order.objects.filter(active=True)
    inactive_orders = Order.objects.exclude(active=True)
    #orders = [('Active', active_orders), ('Inactive', inactive_orders)]
    orders = active_orders | inactive_orders
    orders = orders.order_by('-active', '-date')

    #for order in orders:
    #    orders_price[order] = order.get_total_sum()

    form.fields["orders"].queryset = orders
    return render(request, 'manage_order.html', {'form': form, 'is_admin': is_admin(request), 'orders': orders})


# New restaurant
@user_passes_test(lambda u: u.groups.filter(name=settings.FEEDME_ADMIN_GROUP).count() == 1)
def new_restaurant(request, restaurant_id=None):
    if restaurant_id is None:
        restaurant = Restaurant()
    else:
        restaurant = get_object_or_404(Restaurant, pk=restaurant_id)

    if request.method == 'POST':
        form = NewRestaurantForm(request.POST, instance=restaurant)
        if form.is_valid():
            form.save()
            messages.success(request, "Restaurant added")
            return redirect(new_order)
        else:
            form = NewRestaurantForm(request.POST)
    else:
        form = NewRestaurantForm(instance=restaurant)

    return render(request, 'admin.html', {'form': form, 'is_admin': is_admin(request)})


# Edit restaurant
@user_passes_test(lambda u: u.groups.filter(name=settings.FEEDME_ADMIN_GROUP).count() == 1)
def edit_restaurant(request, restaurant_id=None):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    return new_restaurant(request, restaurant)



def new_poll(request):
    if request.method == 'POST':
        form = NewPollForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'New poll added')
            return redirect(index)
        else:
            messages.error(request, 'Form not validated')
    else:
        form = NewPollForm()
        form.fields['question'].initial = "Hvor skal dotKom spise?"
        form.fields['due_date'].initial = get_next_tuesday()

    return render(request, 'admin.html', {'form': form, 'is_admin': is_admin(request)})


# Remove references to this
def get_order_limit():
    order_limit = ManageOrderLimit.objects.all()
    if order_limit:
        order_limit = ManageOrderLimit.objects.get(pk=1)
    else:
        order_limit = ManageOrderLimit()
    return order_limit


# Remove references to this
@user_passes_test(lambda u: u.groups.filter(name=settings.FEEDME_ADMIN_GROUP).count() == 1)
def set_order_limit(request):
    limit = get_order_limit()
    if request.method == 'POST':
        form = ManageOrderLimitForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            limit.order_limit = data['order_limit']
            limit.save()
            messages.success(request, 'Order limit changed')
            return redirect(set_order_limit)
    else:
        form = ManageOrderLimitForm(instance=limit)

    return render(request, 'admin.html', {'form': form, 'is_admin': is_admin(request)})


# Validation of orderline
def check_orderline(request, form, orderline_id=None, buddies=None):
    orderline_exists = False
    if orderline_id is None:
        orderline = OrderLine()
        orderline.creator = User.objects.get(username=form.creator.username)
    else:
        orderline = get_object_or_404(OrderLine, pk=orderline_id)
        orderline_exists = True
    amount = form.price
    users = [orderline.creator]
    if orderline_exists:
        if len(orderline.users.all()) > 0:
            users.extend(orderline.users.all())
    else:
        users.extend(buddies)
    amount = amount / len(users)
    if get_order().use_validation:
        for user in users:
            if not validate_user_funds(user, amount):
                messages.error(request, 'Unsufficient funds caught for %s' % user.get_username())
                return False
    return True


# Check that the user has enough funds
def validate_user_funds(user, amount):
    get_or_create_balance(user)
    return user.balance.get_balance() >= amount


# Handle payment
def handle_payment(request, order):
    orderlines = order.orderline_set.all()

    paid = []
    already_paid = []
    negatives = []

    for orderline in orderlines:
        if not orderline.paid_for:
            if orderline.users.count() > 0:
                #amount = (orderline.get_total_price()) / (orderline.users.count() + 1)
                amount = orderline.get_price_to_pay()
                if orderline.creator not in orderline.users.all():
                    pay(orderline.creator, amount)
                for user in orderline.users.all():
                    pay(user, amount)
                    paid.append(user.get_username())
                    if user.balance.get_balance() < 0:
                        negatives.append(user.get_username())
                orderline.paid_for = True
                orderline.save()
            else:
                pay(orderline.creator, orderline.get_price_to_pay())
                orderline.paid_for = True
                orderline.save()
                paid.append(orderline.creator.get_username())
                if orderline.creator.balance.get_balance() < 0:
                    negatives.append(orderline.creator.get_username())
        else:
            already_paid.append(orderline.creator.get_username())
            if orderline.users.all().count() > 0:
                for user in orderline.users.all():
                    if user.get_username() == orderline.creator.get_username():
                        print('user both in users and creator')
                    else:
                        already_paid.append(user.get_username())
    if len(paid) > 0:
        messages.success(request, 'Paid orderlines for %s.' % ', '.join(paid))
    if len(already_paid) > 0:
        messages.error(request, 'Already paid orderlines for %s.' % ', '.join(already_paid))
    if len(negatives) > 0:
        messages.error(request, 'These users now have negative balances: %s' % ', '.join(negatives))

    order.active = False
    order.save()


# The actual function for payment
def pay(user, amount):
    user.balance.withdraw(amount)  # This returns True/False whether or not the payment was possible.
    user.balance.save()


# Deposit of funds
def handle_deposit(data):
    user = data['user']
    get_or_create_balance(user)
    amount = data['amount']
    if amount >= 0:
        user.user.balance.deposit(amount)
    else:
        user.user.balance.withdraw(amount)


# Get or create balance for a user
def get_or_create_balance(user):
    try:
        user_balance = Balance.objects.get(user=user)
        if user_balance:
            return user_balance.get_balance()
    except:
        balance = Balance()
        balance.user = user
        balance.save()
        return user.balance.get_balance()


# yes
def get_next_tuesday():
    today = date.today()
    day = today.weekday()
    if day < 1:
        diff = timedelta(days=(1 - day))
    elif day > 1:
        diff = timedelta(days=(7 - day + 1))
    else:
        diff = timedelta(days=0)

    return today + diff

def get_next_wednesday():
    today = date.today()
    day = today.weekday()
    if day < 2:
        diff = timedelta(days=(1 - day))
    elif day > 2:
        diff = timedelta(days=(7 - day + 1))
    else:
        diff = timedelta(days=0)

    return today + diff


def is_admin(request):
    return request.user in User.objects.filter(groups__name=settings.FEEDME_ADMIN_GROUP)


# Get users who should be able to join orderlines
def get_orderline_users():
    return User.objects.filter(groups__name=settings.FEEDME_GROUP).order_by('id')


# Gets latest active order
def get_order():
    if Order.objects.all():
        orders = Order.objects.all().order_by('-id')
        for order in orders:
            if order.active:
                return order
    else:
        return False


# Gets latest active poll
def get_poll():
    if Poll.objects.all():
        if Poll.objects.filter(active=True).count() >= 1:
            return Poll.objects.filter(active=True).order_by('-id')[0]
        else:
            return None


# Checks if user is in current order line
def is_in_current_order(order_type, order_id):
    order = get_order()
    if order_type == 'orderline':
        orderline = get_object_or_404(OrderLine, pk=order_id)
        return orderline in order.orderline_set.all()
    elif order_type == 'order':
        order = get_object_or_404(Order, pk=order_id)
        return order in order.order_set.all()
    else:
        return False


# Manually parses users to validate user funds on buddy-add on initial orderline creation
def manually_parse_users(form):
    li = str(form).split('<select')
    potential_users = li[1].split('<option')
    usernames = []
    for user in potential_users:
        if 'selected' in user:
            usernames.append(user.split('>')[1].split('<')[0])
    users = []
    for username in usernames:
        users.append(User.objects.get(username=username))
    return users


# Checks if user is in another orderline
def in_other_orderline(user):
    order = get_order()
    r1 = ""
    r2 = ""
    if order:
        if order.orderline_set:
            if order.orderline_set.filter(creator=user.id):
                r1 = user == order.orderline_set.filter(creator=user.id)[0].creator
            if order.orderline_set.filter(users=user.id):
                r2 = user in order.orderline_set.filter(users=user.id)[0].users.all()
    return r1 or r2
