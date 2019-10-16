# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Kategori')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='item',
            name='avalible',
            field=models.BooleanField(default=False, verbose_name='Til salgs'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='item',
            name='category',
            field=models.ForeignKey(related_name='category', verbose_name='Kategori', blank=True, to='inventory.ItemCategory', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='item',
            name='price',
            field=models.IntegerField(null=True, verbose_name='Pris', blank=True),
            preserve_default=True,
        ),
    ]
