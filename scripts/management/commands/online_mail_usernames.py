# -*- coding: utf-8 -*-

import re

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db.models import Q
from unidecode import unidecode

from apps.authentication.models import OnlineUser


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # We only sync in members of the Komiteer group
        group = Group.objects.get(name="Komiteer")
        # Fetch all users that do not currently have an alias
        nomail = group.user_set.filter(
            Q(online_mail__isnull=True) | Q(online_mail__exact="")
        ).order_by("id")
        # Find a list of all taken email aliases in the system already
        online_mails = OnlineUser.objects.filter(online_mail__isnull=False).exclude(
            online_mail__exact=""
        )
        taken_mails = [u.online_mail for u in online_mails]

        for user in nomail:
            # Decode the full name of the user to plain ascii
            name = unidecode(user.get_full_name()).lower()

            # Users which lack mail or a name are not considered
            if not name or not user.email:
                continue

            # set to empty string so nothing is appended if not needed
            i = ""
            while True:
                # Start with a suggestion that is only lower case name replaced spaces with dots
                suggestion = re.sub(r"\s+", ".", name)
                # Suggestion now contains only lowercase letters, dots and possibly other chars
                # Like dashes. The following regex is a catch-all and removes them.
                suggestion = re.sub(r"[^a-z.]", "", suggestion)
                # Append the differentiation number
                suggestion += str(i)
                if suggestion not in taken_mails:
                    user.online_mail = suggestion
                    user.save()
                    break
                # If the alias already exists, append a number, starting with 2
                else:
                    i = i + 1 if i else 2

        # Then produce a list of "alias: email" for all users in Komiteer
        for user in group.user_set.all():
            if user.online_mail and user.email:
                print("%s: %s" % (user.online_mail, user.email))
