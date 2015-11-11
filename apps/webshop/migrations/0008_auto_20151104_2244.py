# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webshop', '0007_auto_20151104_2240'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productrelation',
            name='product',
        ),
        migrations.RemoveField(
            model_name='productrelation',
            name='product_size',
        ),
        migrations.AddField(
            model_name='productsize',
            name='product',
            field=models.ForeignKey(default=1, to='webshop.Product'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productsize',
            name='stock',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='productsize',
            name='description',
            field=models.CharField(max_length=50, null=True, verbose_name='Beskrivelse', blank=True),
        ),
        migrations.DeleteModel(
            name='ProductRelation',
        ),
    ]
