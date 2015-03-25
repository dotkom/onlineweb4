# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webshop', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'Kategori', 'verbose_name_plural': 'Kategorier'},
        ),
        migrations.AlterModelOptions(
            name='order',
            options={'verbose_name': 'Bestilling', 'verbose_name_plural': 'Bestillinger'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'verbose_name': 'Produkt', 'verbose_name_plural': 'Produkter'},
        ),
        migrations.AlterModelOptions(
            name='productimage',
            options={'verbose_name': 'Produktbilde', 'verbose_name_plural': 'Produktbilder'},
        ),
    ]
