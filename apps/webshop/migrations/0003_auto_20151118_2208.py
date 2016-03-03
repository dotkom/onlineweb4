# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webshop', '0002_orderline_stripe_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'Kategori', 'verbose_name_plural': 'Kategorier', 'permissions': (('view_category', 'View Category'),)},
        ),
        migrations.AlterModelOptions(
            name='order',
            options={'verbose_name': 'Bestilling', 'verbose_name_plural': 'Bestillinger', 'permissions': (('view_order', 'View Order'),)},
        ),
        migrations.AlterModelOptions(
            name='orderline',
            options={'permissions': (('view_order_line', 'View Order Line'),)},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'verbose_name': 'Produkt', 'verbose_name_plural': 'Produkter', 'permissions': (('view_product', 'View Product'),)},
        ),
        migrations.AddField(
            model_name='orderline',
            name='delivered',
            field=models.BooleanField(default=False),
        ),
    ]
