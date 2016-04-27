# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.core.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'verbose_name': 'Kategori',
                'verbose_name_plural': 'Kategorier',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price', models.DecimalField(max_digits=10, decimal_places=2, blank=True)),
                ('quantity', models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
            ],
            options={
                'verbose_name': 'Bestilling',
                'verbose_name_plural': 'Bestillinger',
            },
        ),
        migrations.CreateModel(
            name='OrderLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('paid', models.BooleanField(default=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
                ('short', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('images_csv', models.CommaSeparatedIntegerField(default=None, max_length=200, null=True, blank=True)),
                ('price', models.DecimalField(max_digits=10, decimal_places=2)),
                ('stock', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('deadline', models.DateTimeField(null=True, blank=True)),
                ('active', models.BooleanField(default=True)),
                ('category', models.ForeignKey(related_name='products', to='webshop.Category')),
            ],
            options={
                'verbose_name': 'Produkt',
                'verbose_name_plural': 'Produkter',
            },
        ),
        migrations.CreateModel(
            name='ProductSize',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('size', models.CharField(max_length=25, verbose_name='St\xf8rrelse')),
                ('description', models.CharField(max_length=50, null=True, verbose_name='Beskrivelse', blank=True)),
                ('stock', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('product', models.ForeignKey(to='webshop.Product')),
            ],
            options={
                'verbose_name': 'St\xf8rrelse',
                'verbose_name_plural': 'St\xf8rrelser',
            },
        ),
        migrations.AddField(
            model_name='order',
            name='order_line',
            field=models.ForeignKey(related_name='orders', to='webshop.OrderLine'),
        ),
        migrations.AddField(
            model_name='order',
            name='product',
            field=models.ForeignKey(to='webshop.Product'),
        ),
        migrations.AddField(
            model_name='order',
            name='size',
            field=models.ForeignKey(blank=True, to='webshop.ProductSize', null=True),
        ),
    ]
