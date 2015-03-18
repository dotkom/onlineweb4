# -*- coding: utf-8 -*-

from datetime import datetime
from django.db import models
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.exceptions import AppRegistryNotReady
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Restaurant(models.Model):
    restaurant_name = models.CharField(_('name'), max_length=50)
    menu_url = models.URLField(_('menu url'), max_length=250)
    phone_number = models.CharField(_('phone number'), max_length=15)
    email = models.EmailField(_('email address'), blank=True, null=True)
    buddy_system = models.BooleanField(_('Enable buddy system'), default=False)

    def __str__(self):
        return self.restaurant_name


@python_2_unicode_compatible
class Order(models.Model):
    date = models.DateField(_('date'))
    restaurant = models.ForeignKey(Restaurant)
    extra_costs = models.FloatField(_('extra costs'), default=0)
    active = models.BooleanField(_('Order currently active'), default=True)
    use_validation = models.BooleanField(_('Enable funds validation'), default=True)

    def get_total_sum(self):
        s = self.orderline_set.aggregate(models.Sum('price'))['price__sum']
        if s is None:
            s = 0
        return s + self.extra_costs

    def get_extra_costs(self):
        users = self.orderline_set.aggregate(models.Sum('users'))['users__sum']
        return self.extra_costs / users

    def order_users(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return User.objects.filter(groups__name=settings.FEEDME_GROUP)

    def available_users(self):
        order_users = self.order_users()
        taken_users = self.taken_users()
        available_users = order_users.exclude(id__in=taken_users)
        return available_users

    def taken_users(self):
        return self.orderline_set.values_list(_('creator'), flat=True)

    def get_latest(self):
        if Order.objects.all():
            orders = Order.objects.all().order_by('-id')
            for order in orders:
                if order.active:
                    return order
        else:
            return False

    def paid(self):
        if self.orderline_set.all():
            for ol in self.orderline_set.all():
                if not ol.paid_for:
                    return False
            return True
        return False

    def __str__(self):
        return "%s @ %s" % (self.date.strftime("%d. %B"), self.restaurant)

    class Meta:
        get_latest_by = 'date'


@python_2_unicode_compatible
class OrderLine(models.Model):
    order = models.ForeignKey(Order)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name=_('owner'))
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name=_('buddies'), null=True, blank=True)
    menu_item = models.CharField(_('menu item'), max_length=50)
    soda = models.CharField(_('soda'), blank=True, null=True, max_length=25)
    extras = models.CharField(_('extras/comments'), blank=True, null=True, max_length=50)
    price = models.IntegerField(_('price'), max_length=4)
    paid_for = models.BooleanField(_('paid for'), default=False)

    def get_order(self):
        return self.order

    def get_users(self):
        return self.users

    def get_buddies(self):
        return self.get_users()

    def get_num_users(self):
        return self.get_users().count()

    def get_total_price(self):
        return (self.order.get_extra_costs() * self.get_num_users()) + self.price

    def get_price_to_pay(self):
        return self.get_total_price() / self.get_num_users()

    def __str__(self):
        return self.creator.get_username()

    @models.permalink
    def get_absolute_url(self):
        return ('edit', (), {'orderline_id': self.id})

    class Meta:
        verbose_name = _('Order line')
        verbose_name_plural = _('Order lines')


@python_2_unicode_compatible
class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    amount = models.FloatField(_('amount'), default=0)
    date = models.DateTimeField(_('transaction date'), auto_now_add=True)

    def __str__(self):
        return self.user.get_username()


@python_2_unicode_compatible
class Balance(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)

    def get_balance(self):
        if self.user.transaction_set.aggregate(models.Sum('amount'))['amount__sum'] is None:
            self.add_transaction(0)
        return self.user.transaction_set.aggregate(models.Sum('amount'))['amount__sum']

    def get_balance_string(self):
        return "%.2f kr" % self.get_balance()

    def add_transaction(self, amount):
        transaction = Transaction()
        transaction.user = self.user
        transaction.amount = amount
        transaction.save()
        return True

    def deposit(self, amount):
        return self.add_transaction(amount)
        # print('Deprecated notice, please add new transaction objects rather than calling the Balance object')

    def withdraw(self, amount):
        return self.add_transaction(amount * -1)
        # print('Deprecated notice, please add new transaction objects rather than calling the Balance object')

    def __str__(self):
        return "%s: %s" % (self.user, self.get_balance())



@python_2_unicode_compatible
class Poll(models.Model):
    question = models.CharField(_('question'), max_length=250)
    active = models.BooleanField(_('active'), default=True)
    due_date = models.DateTimeField(_('due date'))

    def deactivate(self):
        self.active = False
        self.save()

    def activate(self):
        if datetime.now() < self.due_date:
            self.active = True
            self.save()
        # Throw some exception if fails?

    @classmethod
    def get_active(self):
        if Poll.objects.count() == 0:
            return None
        if Poll.objects.latest('id').active:
            return Poll.objects.latest('id')
        else:
            return None

    def get_result(self):
        answers = Answer.objects.filter(poll=self)
        r = dict()
        for answer in answers:
            if answer.answer not in r:
                r[answer.answer] = 0
            r[answer.answer] += 1
        return r

    def get_winner(self):
        winner = (None,-1)
        results = self.get_result()
        for key in results:
            if results[key] > winner[1]:
                winner = (key, results[key])
        return winner[0]

    def __str__(self):
        return "%s due %s" % (self.question, self.due_date.strftime("%x"))


@python_2_unicode_compatible
class Answer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name=_('user'))
    poll = models.ForeignKey(Poll, related_name=_('votes'))
    answer = models.ForeignKey(Restaurant, related_name=_('answer'))

    def __str__(self):
        return "%s: %s (%s)" % (self.user, self.answer, self.poll)


class ManageBalance(models.Model):
    user = models.ForeignKey(Balance)
    amount = models.FloatField(_('amount'), default=0)


class ManageOrders(models.Model):
    orders = models.OneToOneField(Order, related_name=_('Orders'))


class ManageUsers(models.Model):
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name=_('Users'))


class ManageOrderLimit(models.Model):
    order_limit = models.IntegerField(_('Order limit'), default=100)
