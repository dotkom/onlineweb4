# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0011_responsiveimage_photographer'),
        ('inventory', '0004_auto_20160110_2140'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='image',
            field=models.ForeignKey(default=None, blank=True, to='gallery.ResponsiveImage', null=True, on_delete=models.CASCADE),
        ),
    ]
