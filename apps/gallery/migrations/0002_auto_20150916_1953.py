# -*- coding: utf-8 -*-


import datetime

from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='responsiveimage',
            name='date',
        ),
        migrations.AddField(
            model_name='responsiveimage',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 16, 17, 53, 35, 899762, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
