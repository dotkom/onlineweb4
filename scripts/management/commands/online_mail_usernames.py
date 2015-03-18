# -*- coding: utf-8 -*-

import pytz
import datetime

from django.contrib.auth.models import Group
from django.db.utils import IntegrityError
from django.core.management.base import NoArgsCommand, CommandError
from django.utils import timezone

from unidecode import unidecode

from apps.authentication.models import OnlineUser


class Command(NoArgsCommand):

    def handle_noargs(self, *args, **kwargs):
        group = Group.objects.get(name = "Komiteer")
        nomail = group.user_set.filter(online_mail__isnull=True).order_by('id')
        taken_mails = [u.online_mail for u in OnlineUser.objects.filter(online_mail__isnull=False)]

        for user in nomail:
            i = ''
            name = unidecode(user.get_full_name())

            if not name or not email:
                continue

            while True:
                suggestion = name.replace(" ", ".") + str(i)
                if suggestion not in taken_mails:
                    user.online_mail = suggestion
                    user.save()
                    break
                else:
                    i = i + 1 if i else 2

        for user in group.user_set.all():
            if user.online_mail and user.email:
                print "%s: %s" % (user.online_mail, user.email)
