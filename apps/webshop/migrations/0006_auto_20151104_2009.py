# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0011_responsiveimage_photographer'),
        ('webshop', '0005_auto_20151007_2142'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productimage',
            name='product',
        ),
        migrations.AddField(
            model_name='product',
            name='images',
            field=models.ManyToManyField(default=None, to='gallery.ResponsiveImage', null=True, blank=True),
        ),
        migrations.DeleteModel(
            name='ProductImage',
        ),
    ]
