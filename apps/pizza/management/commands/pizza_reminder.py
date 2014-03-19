# -*- coding: utf-8 -*-

from django.core.management.base import NoArgsCommand
from django.contrib.auth.models import Group
from django.db import models
from django.core.mail import send_mail
from pizzasystem.models import Order, Saldo

class Command(NoArgsCommand):
    def handle_noargs(self, **kwargs):
            send_mail(subject, message, from_email, recipient_list())

subject = "Husk å bestille Pizza!"
message = "Hei\n Du har ikke enda lagt inn pizza bestilling for onsdagens dotKom møte. \n Husk å legg den inn i tide! \n mvh Pizzasystemet"
from_email = "dotkom@online.ntnu.no"

def recipient_list():
    users = Order.objects.all().latest().free_users()
    list = []
    for u in users:
        list.append(u.email)
    return list


