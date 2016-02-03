# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.utils import timezone

def set_jobmail_field(apps, schema_editor):
    OnlineUser = apps.get_model("authentication", "OnlineUser")
    AllowedUsername = apps.get_model("authentication", "AllowedUsername")
    for user in OnlineUser.objects.all():
        if AllowedUsername.objects.filter(username=user.ntnu_username).filter(expiration_date__gte=timezone.now()).count() > 0:
            user.jobmail = True
            user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0005_onlineuser_jobmail'),
    ]

    operations = [
        migrations.RunPython(set_jobmail_field),
    ]
