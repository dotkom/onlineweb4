# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Balance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ManageBalance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.FloatField(default=0, verbose_name='amount')),
                ('user', models.ForeignKey(to='feedme.Balance')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ManageOrderLimit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order_limit', models.IntegerField(default=100, verbose_name='Order limit')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ManageOrders',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ManageUsers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('users', models.ManyToManyField(related_name='Users', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(verbose_name='date')),
                ('extra_costs', models.FloatField(default=0, verbose_name='extra costs')),
                ('active', models.BooleanField(default=True, verbose_name='Order currently active')),
            ],
            options={
                'get_latest_by': 'date',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrderLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('menu_item', models.IntegerField(max_length=2, verbose_name='menu item')),
                ('soda', models.CharField(max_length=25, null=True, verbose_name='soda', blank=True)),
                ('extras', models.CharField(max_length=50, null=True, verbose_name='extras/comments', blank=True)),
                ('price', models.IntegerField(default=100, max_length=4, verbose_name='price')),
                ('paid_for', models.BooleanField(default=False, verbose_name='paid for')),
                ('creator', models.ForeignKey(related_name='owner', to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(to='feedme.Order')),
                ('users', models.ManyToManyField(related_name='buddies', null=True, to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'verbose_name': 'Order line',
                'verbose_name_plural': 'Order lines',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('restaurant_name', models.CharField(max_length=50, verbose_name='name')),
                ('menu_url', models.URLField(max_length=250, verbose_name='menu url')),
                ('phone_number', models.CharField(max_length=15, verbose_name='phone number')),
                ('email', models.EmailField(max_length=75, null=True, verbose_name='email address', blank=True)),
                ('buddy_system', models.BooleanField(default=False, verbose_name='Enable buddy system')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.FloatField(default=0, verbose_name='amount')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='transaction date')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='order',
            name='restaurant',
            field=models.ForeignKey(to='feedme.Restaurant'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='manageorders',
            name='orders',
            field=models.OneToOneField(related_name='Orders', to='feedme.Order'),
            preserve_default=True,
        ),
    ]
