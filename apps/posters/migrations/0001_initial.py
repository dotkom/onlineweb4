# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('companyprofile', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Poster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.TextField(max_length=50, verbose_name='arrangementstittel')),
                ('location', models.TextField(max_length=50, verbose_name='sted')),
                ('when', models.DateTimeField(verbose_name='event-start')),
                ('category', models.IntegerField(verbose_name='type', choices=[(0, 'Plakat'), (1, 'Banner'), (2, 'Bong')])),
                ('description', models.TextField(max_length=1000, verbose_name='beskrivelse')),
                ('display_from', models.DateField(verbose_name='vis fra')),
                ('display_to', models.DateField(verbose_name='vis til')),
                ('ordered_date', models.DateTimeField(auto_now_add=True)),
                ('comments', models.TextField(max_length=500, verbose_name='kommentar')),
                ('assigned_to', models.ForeignKey(related_name='tilordnet til', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('company', models.ForeignKey(related_name='bedrift', to='companyprofile.Company')),
                ('ordered_by', models.ForeignKey(related_name='bestilt av', to=settings.AUTH_USER_MODEL)),
                ('ordered_by_group', models.ForeignKey(related_name='bestilt av komite', to='auth.Group')),
            ],
            options={
                'verbose_name': 'plakatbestilling',
                'verbose_name_plural': 'plakatbestillinger',
                'permissions': (('add_poster_order', 'View poster orders'), ('overview_poster_order', 'View poster order overview'), ('view_poster_order', 'View poster orders')),
            },
            bases=(models.Model,),
        ),
    ]
