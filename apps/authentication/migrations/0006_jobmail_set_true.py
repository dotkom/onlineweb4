# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def set_jobmail_field(apps, schema_editor):
    OnlineUser = apps.get_model("authentication", "OnlineUser")
    for user in OnlineUser.objects.all():
        user.jobmail = True
        user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0005_onlineuser_jobmail'),
    ]

    operations = [
        migrations.RunPython(set_jobmail_field),
    ]
