# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webshop', '0008_auto_20151104_2244'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productsize',
            options={'verbose_name': 'St\xf8rrelse', 'verbose_name_plural': 'St\xf8rrelser'},
        ),
        migrations.AddField(
            model_name='order',
            name='size',
            field=models.ForeignKey(to='webshop.ProductSize', null=True),
        ),
    ]
