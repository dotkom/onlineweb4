# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0005_auto_20151018_1008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='gallery.ResponsiveImage', null=True),
            preserve_default=True,
        ),
    ]
