# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filebrowser.fields


class Migration(migrations.Migration):

    replaces = [(b'companyprofile', '0001_initial'), (b'companyprofile', '0002_auto_20151014_2132'), (b'companyprofile', '0003_company_image')]

    dependencies = [
        ('gallery', '0003_auto_20151015_0010'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='bedriftsnavn')),
                ('short_description', models.TextField(max_length=200, verbose_name='kort beskrivelse')),
                ('long_description', models.TextField(null=True, verbose_name='utdypende beskrivelse', blank=True)),
                ('site', models.CharField(max_length=100, verbose_name='hjemmeside')),
                ('email_address', models.EmailField(max_length=75, null=True, verbose_name='epostaddresse', blank=True)),
                ('phone_number', models.CharField(max_length=20, null=True, verbose_name='telefonnummer', blank=True)),
                ('image', models.ForeignKey(null=True, default=None, to='gallery.ResponsiveImage')),
            ],
            options={
                'verbose_name': 'Bedrift',
                'verbose_name_plural': 'Bedrifter',
                'permissions': (('view_company', 'View Company'),),
            },
            bases=(models.Model,),
        ),
    ]
