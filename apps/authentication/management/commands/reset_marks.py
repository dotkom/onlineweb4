# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    help = 'Nullstiller prikkegodkjenning på alle brukere'

    def handle_noargs(self, **options):
        from apps.authentication.models import OnlineUser

        for user in OnlineUser.objects.all():
            user.mark_rules = False
            user.save()
