# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='privacy',
            name='user',
            field=models.OneToOneField(related_name='privacy', to=settings.AUTH_USER_MODEL),
        ),
    ]
