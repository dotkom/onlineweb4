# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0012_auto_20160128_1719'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='stripe_key_index',
        ),
        migrations.AddField(
            model_name='payment',
            name='stripe_key',
            field=models.CharField(default=b'arrkom', max_length=10, verbose_name='stripe key', choices=[(b'arrkom', b'pk_test_replace_this'), (b'prokom', b'pk_test_Ur8B7E5uvheMlpOUVu9SGGbn'), (b'trikom', b'pk_test_bziEErlw9KmTHcNeC6cBXHhw')]),
        ),
    ]
