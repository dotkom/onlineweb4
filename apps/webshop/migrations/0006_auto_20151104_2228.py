# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webshop', '0005_auto_20151007_2142'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('product', models.ForeignKey(to='webshop.Product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductSize',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('size', models.CharField(max_length=25, verbose_name='St\xf8relse')),
                ('description', models.CharField(max_length=50, verbose_name='Beskrivelse')),
                ('stock', models.PositiveSmallIntegerField(null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='productrelation',
            name='product_size',
            field=models.ForeignKey(to='webshop.ProductSize'),
        ),
    ]
