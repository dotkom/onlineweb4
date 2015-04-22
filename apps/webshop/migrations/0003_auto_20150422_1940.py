# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webshop', '0002_auto_20150325_2219'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='slug',
            field=models.SlugField(default=1, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='slug',
            field=models.SlugField(default=1, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='order',
            name='order_line',
            field=models.ForeignKey(related_name='orders', to='webshop.OrderLine'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(related_name='products', to='webshop.Category'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=models.ImageField(upload_to=b'images/webshop'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='productimage',
            name='product',
            field=models.ForeignKey(related_name='images', to='webshop.Product'),
            preserve_default=True,
        ),
    ]
