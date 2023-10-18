# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, timezone

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from apps.authentication.models import Membership


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        now = self.now()
        expiration_date = now
        note = ""

        if len(args) != 1:
            self.stdout.write(
                "Error: You need to specify a filename as the first argument."
            )
            return
        filename = args[0]
        f = open(filename, "r")

        new_count = 0
        update_count = 0

        for line in f:
            line = line.strip()
            # skip empty lines
            if not line:
                continue
            # set the correct expiry date according to FOS.
            if line == "MIT" or line == "mit":
                expiration_date = now + timedelta(days=365 * 2)
                note = "Master %d" % now.year
                continue
            if line == "BIT" or line == "bit":
                expiration_date = now + timedelta(days=365 * 3)
                note = "Bachelor %d" % now.year
                continue

            try:
                entry = Membership(
                    username=line,
                    registered=now,
                    note=note,
                    description="Added by script.",
                    expiration_date=expiration_date,
                )
                entry.save()

                new_count = new_count + 1
            except IntegrityError:
                au = Membership.objects.get(username=line)
                au.expiration_date = expiration_date
                au.save()

                update_count = update_count + 1

        if new_count > 0:
            self.stdout.write("%d new memberships added" % new_count)
        if update_count > 0:
            self.stdout.write("%d memberships updated" % update_count)

    def now(self):
        now = timezone.now()
        now = datetime(now.year, 9, 15, 0, 0)
        # subtract a year if we're adding people with this script in the spring
        if now.month < 6:
            now = now - timedelta(days=365)
        now = now.astimezone()
        return now
