# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=45, verbose_name='Tittel')),
                ('description', models.CharField(max_length=100, verbose_name='Beskrivelse')),
                ('completed', models.BooleanField(default=False, verbose_name='Ferdigstilt')),
                ('completed_date', models.DateTimeField(null=True, verbose_name='Ferdigstilt dato', blank=True)),
                ('deadline', models.DateTimeField(null=True, verbose_name='Tidsfrist', blank=True)),
                ('group', models.ForeignKey(to='auth.Group')),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
