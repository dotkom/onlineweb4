# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0002_auto_20150415_2055'),
        ('posters', '0009_auto_20150409_0746'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomText',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field', models.CharField(max_length=50)),
                ('text', models.CharField(max_length=30)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrderMixin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ordered_date', models.DateTimeField(auto_now_add=True)),
                ('comments', models.TextField(max_length=500, null=True, verbose_name='kommentar', blank=True)),
                ('amount', models.IntegerField(null=True, verbose_name='antall', blank=True)),
                ('finished', models.BooleanField(default=False, verbose_name='ferdig')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Freestyle',
            fields=[
                ('ordermixin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='posters.OrderMixin')),
                ('description', models.TextField(max_length=1000, verbose_name='beskrivelse')),
            ],
            options={
            },
            bases=('posters.ordermixin',),
        ),
        migrations.CreateModel(
            name='EventMixin',
            fields=[
                ('ordermixin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='posters.OrderMixin')),
                ('event', models.ForeignKey(related_name='Arrangement', to='events.Event')),
            ],
            options={
            },
            bases=('posters.ordermixin',),
        ),
        migrations.AddField(
            model_name='ordermixin',
            name='assigned_to',
            field=models.ForeignKey(related_name='tilordnet til', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordermixin',
            name='ordered_by',
            field=models.ForeignKey(related_name='bestilt av', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordermixin',
            name='ordered_committee',
            field=models.ForeignKey(related_name='bestilt av komite', to='auth.Group'),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='poster',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='poster',
            name='assigned_to',
        ),
        migrations.RemoveField(
            model_name='poster',
            name='category',
        ),
        migrations.RemoveField(
            model_name='poster',
            name='comments',
        ),
        migrations.RemoveField(
            model_name='poster',
            name='company',
        ),
        migrations.RemoveField(
            model_name='poster',
            name='finished',
        ),
        migrations.RemoveField(
            model_name='poster',
            name='id',
        ),
        migrations.RemoveField(
            model_name='poster',
            name='location',
        ),
        migrations.RemoveField(
            model_name='poster',
            name='ordered_by',
        ),
        migrations.RemoveField(
            model_name='poster',
            name='ordered_committee',
        ),
        migrations.RemoveField(
            model_name='poster',
            name='ordered_date',
        ),
        migrations.RemoveField(
            model_name='poster',
            name='title',
        ),
        migrations.RemoveField(
            model_name='poster',
            name='when',
        ),
        migrations.AddField(
            model_name='poster',
            name='eventmixin_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, default=1, serialize=False, to='posters.EventMixin'),
            preserve_default=False,
        ),
    ]
