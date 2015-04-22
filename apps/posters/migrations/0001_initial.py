# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('events', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
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
            ],
            options={
            },
            bases=('posters.ordermixin',),
        ),
        migrations.CreateModel(
            name='Poster',
            fields=[
                ('eventmixin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='posters.EventMixin')),
                ('description', models.TextField(max_length=1000, verbose_name='beskrivelse')),
                ('price', models.DecimalField(null=True, verbose_name='pris', max_digits=10, decimal_places=2, blank=True)),
                ('display_from', models.DateField(verbose_name='vis fra')),
                ('display_to', models.DateField(verbose_name='vis til')),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': 'plakatbestilling',
                'verbose_name_plural': 'plakatbestillinger',
                'permissions': (('add_poster_order', 'Add poster orders'), ('overview_poster_order', 'View poster order overview'), ('view_poster_order', 'View poster orders')),
            },
            bases=('posters.eventmixin',),
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
        migrations.AddField(
            model_name='eventmixin',
            name='event',
            field=models.ForeignKey(related_name='Arrangement', to='events.Event'),
            preserve_default=True,
        ),
    ]
