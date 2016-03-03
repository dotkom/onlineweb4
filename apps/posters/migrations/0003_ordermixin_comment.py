# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posters', '0002_auto_20150926_2324'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordermixin',
            name='comments',
            field=models.TextField(max_length=1000, null=True, verbose_name='kommentarer', blank=True),
        ),
    ]
