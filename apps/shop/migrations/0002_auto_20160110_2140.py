# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderline',
            name='user',
            field=models.ForeignKey(related_name='u', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
        ),
    ]
