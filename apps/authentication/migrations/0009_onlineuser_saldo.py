# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0008_auto_20151014_2156'),
    ]

    operations = [
        migrations.AddField(
            model_name='onlineuser',
            name='saldo',
            field=models.IntegerField(default=0, verbose_name='saldo'),
            preserve_default=True,
        ),
    ]
