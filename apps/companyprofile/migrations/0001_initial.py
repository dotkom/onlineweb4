# -*- coding: utf-8 -*-


from django.db import models, migrations
import filebrowser.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='bedriftsnavn')),
                ('short_description', models.TextField(max_length=200, verbose_name='kort beskrivelse')),
                ('long_description', models.TextField(null=True, verbose_name='utdypende beskrivelse', blank=True)),
                ('image', filebrowser.fields.FileBrowseField(max_length=200, verbose_name='bilde')),
                ('site', models.CharField(max_length=100, verbose_name='hjemmeside')),
                ('email_address', models.EmailField(max_length=75, null=True, verbose_name='epostaddresse', blank=True)),
                ('phone_number', models.CharField(max_length=20, null=True, verbose_name='telefonnummer', blank=True)),
            ],
            options={
                'verbose_name': 'Bedrift',
                'verbose_name_plural': 'Bedrifter',
                'permissions': (('view_company', 'View Company'),),
            },
            bases=(models.Model,),
        ),
    ]
