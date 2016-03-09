# -*- coding: utf-8 -*-

from apps.authentication.models import OnlineUser as User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        guests = User.objects.filter(field_of_study=0)
        for guest in guests:
            guest.infomail = False
            guest.save()
