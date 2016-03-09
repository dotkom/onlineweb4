# -*- coding: utf-8 -*-


import datetime

from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('splash', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='splashyear',
            name='start_date',
            field=models.DateField(default=datetime.datetime(2015, 4, 22, 20, 14, 54, 144759, tzinfo=utc), verbose_name='start_date'),
            preserve_default=False,
        ),
    ]
