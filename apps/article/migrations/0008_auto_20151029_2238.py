# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0007_auto_20151029_2233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='authors',
            field=models.CharField(max_length=200, verbose_name='forfatter(e)', blank=True),
        ),
    ]
