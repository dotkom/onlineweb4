# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posters', '0005_poster_bong'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneralOrder',
            fields=[
                ('ordermixin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='posters.OrderMixin')),
                ('title', models.CharField(max_length=60, verbose_name='arrangementstittel')),
            ],
            options={
            },
            bases=('posters.ordermixin',),
        ),
        migrations.RemoveField(
            model_name='freestyle',
            name='ordermixin_ptr',
        ),
        migrations.DeleteModel(
            name='Freestyle',
        ),
        migrations.RemoveField(
            model_name='ordermixin',
            name='comments',
        ),
        migrations.RemoveField(
            model_name='poster',
            name='description',
        ),
        migrations.AddField(
            model_name='ordermixin',
            name='description',
            field=models.TextField(max_length=1000, null=True, verbose_name='beskrivelse', blank=True),
            preserve_default=True,
        ),
    ]
