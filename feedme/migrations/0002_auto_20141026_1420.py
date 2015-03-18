# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('feedme', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('answer', models.ForeignKey(related_name='answer', to='feedme.Restaurant')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question', models.CharField(max_length=250, verbose_name='question')),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('due_date', models.DateTimeField(verbose_name='due date')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='answer',
            name='poll',
            field=models.ForeignKey(related_name='poll', to='feedme.Poll'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='answer',
            name='user',
            field=models.ForeignKey(related_name='user', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
