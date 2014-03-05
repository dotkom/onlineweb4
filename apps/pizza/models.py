# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
#from django.contrib.auth import get_user_model

User = getattr(settings, 'AUTH_USER_MODEL', 'auth.User') 

class OrderLine(models.Model):
    date = models.DateField(_("dato"))
    total_sum = models.IntegerField(_("Sum"), max_length=4, default=0)

    def pizza_users(self):
        return User.objects.filter(groups__name=settings.PIZZA_GROUP)

    def used_users(self):
        users = []
        for pizza in self.pizza_set.all():
            users.append(pizza.user)
            if pizza.buddy:
                users.append(pizza.buddy)
        return users

    def free_users(self, buddy=None, pizzauser=None):
        free_users = self.pizza_users()
        for user in self.used_users():
            if not (user == buddy or user == pizzauser):
                free_users = free_users.exclude(id=user.id)
        return free_users

    def __unicode__(self):
        return self.date.strftime("%d-%m-%Y")

    class Meta:
        get_latest_by = 'date'
    
class Pizza(models.Model):
    order_line = models.ForeignKey(OrderLine)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="Owner")
    need_buddy = models.BooleanField(_('Trenger Buddy'), default=False)
    buddy = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="Pizzabuddy", null=True, blank=True)
    soda = models.CharField(_('brus'), blank=True, null=True, default='cola', max_length=25)
    dressing = models.BooleanField(_(u'hvitløksdressing'), default=True)
    pizza = models.IntegerField(_('pizzanummer'), max_length=2, default=8)

    def __unicode__(self):
        return self.user.username
    
    @models.permalink
    def get_absolute_url(self):
        return ('edit', (), {'pizza_id' : self.id})

    class Meta:
        verbose_name = _('Pizza')
        verbose_name_plural = _('Pizzar')

class Order(models.Model):
    order_line = models.ForeignKey(OrderLine)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    content = models.TextField(_(u'beskrivelse'))

    def __unicode__(self):
        return self.user.username

class Saldo(models.Model):
    saldo = models.FloatField(_('saldo'), default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

class ManageOrderLines(models.Model):
    order_lines = models.OneToOneField(OrderLine, related_name=_('Ordre'))
    total_sum = models.IntegerField(_('Total regning'), max_length=4)

class ManageUsers(models.Model):
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name=_('Brukere'))
    #users.help_text = ''
    add_value = models.IntegerField(_('Verdi'), max_length=4)
    add_value.help_text = _(u'Legger til verdien på alle valgte brukere') 


class ManageOrderLimit(models.Model):
    order_limit = models.IntegerField(_('Bestillings grense'), default=100)
    
