# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0010_auto_20151031_0348'),
    ]

    operations = [
        migrations.AddField(
            model_name='responsiveimage',
            name='photographer',
            field=models.CharField(default=b'', max_length=100, verbose_name='Fotograf', blank=True),
        ),
    ]
