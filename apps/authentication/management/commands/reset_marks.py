# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Nullstiller prikkegodkjenning på alle brukere'

    def handle(self, **options):
        from apps.authentication.models import OnlineUser

        for user in OnlineUser.objects.all():
            user.mark_rules = False
            user.save()
