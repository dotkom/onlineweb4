# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0003_auto_20151015_0010'),
    ]

    operations = [
        migrations.AddField(
            model_name='responsiveimage',
            name='description',
            field=models.TextField(default=b'', max_length=2048, verbose_name='Beskrivelse', blank=True),
            preserve_default=True,
        ),
    ]
